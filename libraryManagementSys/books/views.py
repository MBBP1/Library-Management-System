from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Book, Member, BorrowRecord
from .forms import BookForm, MemberForm, BorrowForm
from django.contrib.auth.decorators import login_required
from books.oldcode.library_logic import Library, Book as OldBook, Member as OldMember  # Importer gammel kode
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime, timedelta
from .models import Reservation
from django.contrib.auth.models import Group
from django.db.models import Q  # Import Q for komplekse forespørgsler
from datetime import timedelta, date
from .models import Member


# Initialiser biblioteket fra den gamle kode
library = Library()

def librarian_required(view_func):
    return user_passes_test(lambda u: u.groups.filter(name='Librarian').exists())(view_func)

def base_context_processor(request):
    return {
        'is_librarian': request.user.is_authenticated and request.user.groups.filter(name='Librarian').exists()
    }


@login_required
def home(request):
    books = Book.objects.all()
    return render(request, 'books/home.html', {'books': books})

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/book_detail.html', {'book': book})


@librarian_required
@login_required
def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn')
        publisher = request.POST.get('publisher')
        publication_date = request.POST.get('publication_date')
        quantity = int(request.POST.get('quantity', 1))
        available = int(request.POST.get('available', quantity))  # Default available to total copies
        category = request.POST.get('category')

        # Ensure available copies do not exceed total copies
        if available > quantity:
            messages.error(request, "Available copies cannot exceed total copies.")
            return render(request, 'books/add_book.html')

        # Create and save the book in the database
        Book.objects.create(
            title=title,
            author=author,
            isbn=isbn,
            publisher=publisher,
            publication_date=publication_date,
            quantity=quantity,
            available=available,
            category=category
        )

        messages.success(request, f"The book '{title}' by {author} has been added successfully.")
        return redirect('manage_books')
    return render(request, 'books/add_book.html')

@login_required
def return_book(request, book_id):
    # Debugging: Udskriv alle aktive BorrowRecords for den loggede ind bruger
    active_records = BorrowRecord.objects.filter(
        member__user=request.user,
        return_date__isnull=True
    )
    print("Active BorrowRecords for user:", active_records)

    # Find BorrowRecord for den loggede ind bruger og den specifikke bog
    record = BorrowRecord.objects.filter(
        book__id=book_id,
        member__user=request.user,
        return_date__isnull=True
    ).first()

    if record:
        if request.method == 'POST':
            # Hent bogens tilstand fra formularen
            condition = request.POST.get('condition', 'good')
            record.return_date = date.today()
            record.condition = condition
            record.fine = record.calculate_fine()  # Beregn bøde
            record.save()

            # Opdater bogens tilgængelighed
            record.book.available += 1
            record.book.save()

            # Kald notify_reserved_users for at opdatere reservationer
            if record.book.available > 0:
                print(f"Calling notify_reserved_users for book: {record.book.title}")  # Debugging
                record.book.notify_reserved_users()

            messages.success(request, f"You have returned '{record.book.title}'. Fine: ${record.fine}.")
            return redirect('my_borrowed_books')

        return render(request, 'books/return_book.html', {'record': record})
    else:
        messages.error(request, "You cannot return this book.")
        print(f"Debug: No matching BorrowRecord found for book_id={book_id} and user={request.user.username}")
        return redirect('my_borrowed_books')

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    member = request.user.member

    # Check if the user has already borrowed the book
    if BorrowRecord.objects.filter(book=book, member=member, return_date__isnull=True).exists():
        messages.error(request, f"You have already borrowed '{book.title}'.")
        return redirect('my_borrowed_books')

    # Check if the book is available
    if book.available > 0:
        # Remove the reservation if it exists
        reservation = Reservation.objects.filter(book=book, member=member).first()
        if reservation:
            print(f"Removing reservation for book: {book.title}, user: {member.user.username}")  # Debugging
            reservation.delete()

        # Create a borrow record
        BorrowRecord.objects.create(
            book=book,
            member=member,
            due_date=datetime.now() + timedelta(days=14)  # 14-day borrowing period
        )
        book.available -= 1
        book.save()
        messages.success(request, f"You have successfully borrowed '{book.title}'.")
    else:
        messages.error(request, f"'{book.title}' is not available for borrowing.")

    return redirect('my_borrowed_books')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Validate that all fields are filled
        if not username or not first_name or not last_name or not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, 'registration/register.html')

        # Check if the username already exists
        if not User.objects.filter(username=username).exists():
            # Create the User object and assign it to the "user" variable
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )

            # Automatically create a Member object for the new user
            Member.objects.create(
                user=user,
                membership_number=f"M{user.id:05d}"  # Generate a unique membership number (e.g., M00001)
            )

            messages.success(request, "You have registered successfully.")
            return redirect('login')
        else:
            messages.error(request, "Username already exists.")
    return render(request, 'registration/register.html')

@login_required
def my_borrowed_books(request):
    borrowed_books = BorrowRecord.objects.filter(
        member__user=request.user,
        return_date__isnull=True
    )

    reserved_books = Reservation.objects.filter(
        member__user=request.user
    )
    print(f"Reserved books for user {request.user.username}: {reserved_books}")  # Debugging

    return render(request, 'books/my_borrowed_books.html', {
        'borrowed_books': borrowed_books,
        'reserved_books': reserved_books
    })

def logout_view(request):
    messages.success(request, "You have been logged out successfully.")
    #print(messages.get_messages(request))
    return redirect('login')


@login_required
def reserve_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    member = request.user.member

    # Tjek kun for aktive reservationer
    existing_reservation = Reservation.objects.filter(book=book, member=member).first()
    if existing_reservation:
        messages.error(request, f"You have already reserved '{book.title}'.")
        return redirect('book_detail', pk=book_id)

    # Opret en ny reservation
    Reservation.objects.create(book=book, member=member)
    book.reserved_count += 1
    book.save()
    messages.success(request, f"You have successfully reserved '{book.title}'.")
    return redirect('book_detail', pk=book_id)


@librarian_required
@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.isbn = request.POST.get('isbn')
        book.publisher = request.POST.get('publisher')
        book.publication_date = request.POST.get('publication_date')
        quantity = int(request.POST.get('quantity', book.quantity))
        available = int(request.POST.get('available', book.available))
        book.category = request.POST.get('category', book.category)

        # Ensure available copies do not exceed total copies
        if available > quantity:
            messages.error(request, "Available copies cannot exceed total copies.")
            return render(request, 'books/edit_book.html', {'book': book})

        book.quantity = quantity
        book.available = available
        book.save()

        # Notify users if the book becomes available
        if book.available > 0:
            print(f"Calling notify_reserved_users for book: {book.title}")  # Debugging
            book.notify_reserved_users()

        messages.success(request, f"The book '{book.title}' has been updated successfully.")
        return redirect('manage_books')

    return render(request, 'books/edit_book.html', {'book': book})



@librarian_required
@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    messages.success(request, f"The book '{book.title}' has been deleted successfully.")
    return redirect('manage_books')


@librarian_required
@login_required
def view_borrowing_records(request):
    query = request.GET.get('q', '').strip()  # Get the search query
    borrowing_records = BorrowRecord.objects.all()

    # Filter borrowing records by member's full name or membership number
    if query:
        borrowing_records = borrowing_records.filter(
            Q(member__user__first_name__icontains=query) |
            Q(member__user__last_name__icontains=query) |
            Q(member__membership_number__icontains=query)
        )

    return render(request, 'books/borrowing_records.html', {
        'borrowing_records': borrowing_records,
        'query': query
    })

@librarian_required
@login_required
def manage_books(request):
    books = Book.objects.all()
    return render(request, 'books/manage_books.html', {'books': books})


@librarian_required
@login_required
def edit_books(request):
    books = Book.objects.all()
    return render(request, 'books/edit_books.html', {'books': books})


@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, member__user=request.user)
    print(f"Deleting reservation for book: {reservation.book.title}, user: {reservation.member.user.username}")  # Debugging
    reservation.delete()  # Slet reservationen
    messages.success(request, f"You have successfully canceled your reservation for '{reservation.book.title}'.")
    return redirect('my_borrowed_books')


@login_required
def search_books(request):
    query = request.GET.get('q', '').strip()  # Hent søgestrengen
    category = request.GET.get('category', '').strip()  # Hent kategori
    books = Book.objects.all()

    # Filtrer baseret på søgestreng og kategori
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query) |
            Q(category__icontains=query)
        )
    if category:
        books = books.filter(category__icontains=category)

    return render(request, 'books/search_results.html', {
        'books': books,
        'query': query,
        'category': category
    })


@librarian_required
@login_required
def view_members(request):
    members = Member.objects.all()
    return render(request, 'books/view_members.html', {'members': members})

@librarian_required
@login_required
def edit_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)

    if request.method == 'POST':
        username = request.POST.get('username', member.user.username)
        first_name = request.POST.get('first_name', member.user.first_name)
        last_name = request.POST.get('last_name', member.user.last_name)
        email = request.POST.get('email', member.user.email)

        # Check if the username is unique
        if User.objects.filter(username=username).exclude(id=member.user.id).exists():
            messages.error(request, "The username is already taken. Please choose a different one.")
            return render(request, 'books/edit_member.html', {'member': member})

        # Update the User object
        member.user.username = username
        member.user.first_name = first_name
        member.user.last_name = last_name
        member.user.email = email
        member.user.save()

        messages.success(request, f"Member '{member.user.get_full_name()}' has been updated successfully.")
        return redirect('view_members')

    return render(request, 'books/edit_member.html', {'member': member})
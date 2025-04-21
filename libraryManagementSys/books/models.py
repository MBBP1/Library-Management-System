# This is a Django model for a library management system. It includes models for books, members, and borrow records.

from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail  
from datetime import timedelta, date

class Author(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Publisher(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    publisher = models.CharField(max_length=100)
    publication_date = models.DateField()
    quantity = models.PositiveIntegerField(default=1)
    available = models.PositiveIntegerField(default=1)
    reserved_count = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50)

    def __str__(self):
        return self.title

    def notify_reserved_users(self):
        reservations = self.reservation_set.filter(notified=False)
        print(f"Reservations to notify for book '{self.title}': {reservations}")  # Debugging
        for reservation in reservations:
            print(f"Notifying user: {reservation.member.user.username} for book: {self.title}")  # Debugging
            reservation.notified = True  # Marker som notificeret
            reservation.save()
        print(f"Finished notifying users for book '{self.title}'")  # Debugging

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership_number = models.CharField(max_length=10, unique=True)
    #phone = models.CharField(max_length=15)
    #address = models.TextField()

    def __str__(self):
        return self.user.get_full_name()

class BorrowRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    due_date = models.DateField()
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.member} borrowed {self.book}"


class Reservation(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    reservation_date = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.member} reserved {self.book}"
    

class BorrowRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()  # Forfaldsdato
    return_date = models.DateField(null=True, blank=True)
    fine = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)  # Bøde
    condition = models.CharField(
        max_length=10,
        choices=[('good', 'Good'), ('damaged', 'Damaged'), ('lost', 'Lost')],
        null=True,
        blank=True
    )  # Tilstand ved returnering

    def calculate_fine(self):
        """Beregn bøde baseret på forfaldsdato."""
        if self.return_date and self.return_date > self.due_date:
            overdue_days = (self.return_date - self.due_date).days
            return overdue_days * 10  # $10 per dag
        return 0
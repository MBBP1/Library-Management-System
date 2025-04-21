"""
Library Management System
==========================
This provides a simple Library Management System that allows users to manage books, e-books,
and members within a library.

Features:
- Add, update, remove, and display books and members.
- Borrow and return books with transaction tracking.
- Search books by title or author.
- Display transaction history of members.
- Console-based user interface for interaction.

Author: [Mikkel Bentsen-Petersen]
Date: [2025-03-25]
"""

from datetime import datetime

# Class that represents a physical book in the library.
class Book:
    def __init__(self, book_id, title, author, copies):  # Initializes a book with ID, title, author, and number of copies.
        self.book_id = book_id                           # Unique identifier for the book
        self.title = title                               # Title of the book
        self.author = author                             # Author of the book
        self.copies = copies                             # Number of copies available in the library

    # Method that displays book details.
    def display_info(self):
        print(f"ID: {self.book_id}, Title: {self.title}, Author: {self.author}, Copies: {self.copies}") # Prints the book information.


####################################################################################################################################################################################


# Class that represents an e-book, inheriting from Book. (Polymorphism)
class Ebook(Book):
    def __init__(self, book_id, title, author, file_size):                   # Initializes a e-book with extra attributs for file size
        super().__init__(book_id, title, author, copies=None)                # Calls the constructor of the parent class (Book)
        self.file_size = file_size                                           # File size of the e-book in MB

    # Method that displays e-book details.
    def display_info(self): 
        print(f"ID: {self.book_id}, Title: {self.title}, Author: {self.author}, File Size: {self.file_size} MB") # Prints the e-book information.
                                                                             # Overrides the display_info method of the parent class (Book) to include file size.


####################################################################################################################################################################################


# Class that represents a library member.
class Member:
    def __init__(self, member_id, name):  
        self.member_id = member_id     # ID of the member
        self.name = name               # Name of the member
        self.borrowed_books = []       # List of borrowed books
        self.transaction_history = []  # List of transaction history

    # Method that displays member details.
    def display_info(self): 
        print(f"ID: {self.member_id}, Name: {self.name}, Borrowed Books: {', '.join(self.borrowed_books) if self.borrowed_books else 'None'}") 

    # Method that handles book borrowing.
    def borrow_book(self, book):
        if isinstance(book, Ebook):                                          # If the book is an e-book, it cannot be borrowed. 
            self.borrowed_books.append(book.title)                           # Adds the e-book title to the borrowed books list.
            transaction_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Formats the current time.
            self.transaction_history.append(f"Borrowed Ebook '{book.title}' on {transaction_time}") # Adds the transaction to the history.
            print(f"{self.name} borrowed Ebook '{book.title}'")              # Prints a message that the e-book has been borrowed.
        elif book.copies > 0:                                                # Checks if the book is available for borrowing.
            book.copies -= 1                                                 # Decreases the number of copies available.
            self.borrowed_books.append(book.title)                           # Adds the book title to the borrowed books list.
            transaction_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
            self.transaction_history.append(f"Borrowed '{book.title}' on {transaction_time}")   
            print(f"{self.name} borrowed '{book.title}'")                    # Prints a message that the book has been borrowed.
        else:
            print(f"Sorry, '{book.title}' is not available.")  

    # Method that handles book returning.
    def return_book(self, book):
        if book.title in self.borrowed_books:                                # Checks if the book is in the borrowed books list.
            if not isinstance(book, Ebook):                                  # If the book is not an e-book, increase the number of copies.
                book.copies += 1                                             # Increases the number of copies available.
            self.borrowed_books.remove(book.title)                           # Removes the book from the borrowed books list.
            transaction_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
            self.transaction_history.append(f"Returned '{book.title}' on {transaction_time}") 
            print(f"{self.name} returned '{book.title}'")                    # Prints a message that the book has been returned. 
        else:
            print(f"{self.name} does not have '{book.title}' borrowed.")     # Checks if the book is borrowed by the member.

    # Method that displays transactions history
    def display_transaction_history(self):                                   # Displays the transaction history for the member.
        print(f"\nTransaction History for {self.name}:")                     # Prints the name of the member.
        if self.transaction_history:                                         # Checks if the member has any transaction history. 
            for transaction in self.transaction_history:                     # Loops through the transaction history and prints each transaction.
                print(transaction)
        else:
            print("No transaction history.")


####################################################################################################################################################################################


# Class that manages books and members in the library.
class Library:
    def __init__(self):
        self.books = []                                                      # List of books in the library
        self.members = []                                                    # List of members in the library
        
    # Method that adds a book to the library.
    def add_book(self, book):
        if any(b.book_id == book.book_id for b in self.books):               # Checks if the book already exists in the library.
            print(f"Book/Ebook with ID: {book.book_id} already exists") 
        else:
            self.books.append(book)
            print(f"Book/Ebook '{book.title}' added to the library.")

    # Method that removes a book.
    def remove_book(self, book_id):
        for book in self.books:                                              # Loops through the list of books to find the book with the given ID.
            if book.book_id == book_id:                                      # Checks if the book exists in the library.     
                self.books.remove(book)                                      # Removes the book from the list of books.
                print(f"Book '{book.title}' removed from the library.")
                return 
        print(f"Book with ID {book_id} not found.")
    
    # Method that updates a books book_id, title, author and number of copies or file size. 
    def update_book(self, book_id, title=None, author=None, copies=None, file_size=None): 
        for book in self.books:                                              # Loops through the list of books to find the book with the given ID.
            if book.book_id == book_id:                                      # Checks if the book exists in the library.
                if title:
                    book.title = title                                       # Updates the title of the book.
                if author:
                    book.author = author                                     # Updates the author of the book.
                if isinstance(book, Ebook):                                  # Checks if the book is an e-book.
                    if file_size is not None:                                
                        book.file_size = file_size                           # Updates the file size of the e-book.
                else:
                    if copies is not None:   
                        book.copies = copies                                 # Updates the number of copies of the book.

                print(f"Book '{book_id}' updated successfully.")
                return
        print(f"Book with ID {book_id} not found.")

    # Method that adds a member to the library.
    def add_member(self, member):
        if any(m.member_id == member.member_id for m in self.members):       # Checks if the member already exists in the library.
            print(f"Member with ID: {member.member_id} already exists")
        else:
            self.members.append(member)                                      # Adds the member to the list of members.
            print(f"Member '{member.name}' added to the library.")

    # Method that removees a member from the library.
    def remove_member(self, member_id): 
        for member in self.members:                                          # Loops through the list of members to find the member with the given ID.
            if member.member_id == member_id:                                # Checks if the member exists in the library.
                self.members.remove(member)                                  # Removes the member from the list of members.
                print(f"Member '{member.name}' removed from the library.")
                return
        print(f"Member with ID {member_id} not found.")

    # Method that updates a members name.
    def update_member(self, member_id, new_name):
        for member in self.members:                                          # Loops through the list of members to find the member with the given ID.
            if member.member_id == member_id:                                # Checks if the member exists in the library.
                old_name = member.name                                       # Stores the old name of the member.
                member.name = new_name                                       # Updates the name of the member.
                print(f"Member '{old_name}' renamed to '{new_name}'.")
                return
            print(f"Member with ID {member_id} not found.")

    # Method that displays all books in the library.
    def display_books(self):
        print("\nLibrary Books:")
        for book in self.books:                                              # Loops through the list of books and displays each book's information.
            if isinstance(book, Ebook):                                      # Checks if the book is an e-book.
                print("[Ebook] ", end="")                                    # Prints "[Ebook]" before the book information.
            else:
                print("[Book]  ", end="")                                    # Prints "[Book]" before the book information.
            book.display_info()                                              # Calls the display_info method of the book to print its information.
        #input("\nPress Enter to continue...")

    # Method that shows all members in the library.
    def display_members(self):
        print("\nLibrary Members:")
        for member in self.members:                                          # Loops through the list of members and displays each member's information.
            member.display_info()                                            # Calls the display_info method of the member to print its information.
        #input("\nPress Enter to continue...")

    # Method that allows a member to borrow a book.
    def issue_book(self, member_id, book_id):
        member = next((m for m in self.members if m.member_id == member_id), None)   # Finds the member with the given ID.
        book = next((b for b in self.books if b.book_id == book_id), None)           # Finds the book with the given ID.
        if member and book:                                                          # Checks if both the member and book exist.
            member.borrow_book(book)                                                 # Calls the borrow_book method of the member to borrow the book.
        else:
            print("Invalid member ID or book ID.")

    # Method that allows a member to return a book.
    def return_book(self, member_id, book_id):
        member = next((m for m in self.members if m.member_id == member_id), None)   # Finds the member with the given ID.
        book = next((b for b in self.books if b.book_id == book_id), None)           # Finds the book with the given ID.
        if member and book:                                                          # Checks if both the member and book exist.
            member.return_book(book)                                                 # Calls the return_book method of the member to return the book.
        else:
            print("Invalid member ID or book ID.")

    # Method that allows you to search for a book.
    def search_books(self, search_term):
                                                                                     # Searches for books that match the search term in title or author.
        found_books = [book for book in self.books if search_term.lower() in book.title.lower() or search_term.lower() in book.author.lower()] 
        if found_books:
            print("\nSearch Results:")
            for book in found_books:                                                 # Loops through the found books and displays each book's information.
                book.display_info()                                                  # Calls the display_info method of the book to print its information.
        else:
            print(f"No books found matching '{search_term}'.")
        
        return found_books                                                           # Return the list of found books for further processing if needed.

    # Method that displays transactions history for all members.
    def display_transaction_history(self):
        for member in self.members:                                                  # Loops through the list of members and displays each member's transaction history.
            member.display_transaction_history()                                     # Calls the display_transaction_history method of the member to print its information.
        #input("\nPress Enter to continue...")

'''
####################################################################################################################################################################################


# Function that ensures only integers are accepted and handles invalid input.
def getInt(prompt):                                                             
    while True:                                                                      # Loops until a valid integer is entered.                     
        try:                                                                                                                                           
            return int(input(prompt))                                                # Prompts the user for input and converts it to an integer.
        except ValueError:                                                           # Catches ValueError if the input is not a valid integer.
            print("Invalid input! Please enter a valid number.")


####################################################################################################################################################################################


# Main funktion that runs the Library Management System - [CLI].
def main():
    library = Library()                                                              # Creates an instance of the Library class.


    while True:                                                                      # Main loop that runs the library management system until the user chooses to exit.
        print("\nLibrary Management System") 
        print("0. Add Ebook")
        print("1. Add Book")
        print("2. Add Member")
        print("3. Display Books")
        print("4. Display Members")
        print("5. Issue Book")
        print("6. Return Book")
        print("7. Display Transaction History")
        print("8. Remove Member")
        print("9. Update Member")
        print("10. Update Book")
        print("11. Search For Books")
        print("12. Remove Book")
        print("13. Exit")
        
        choice = input("Enter your choice: ")                                       # Prompts the user for a choice from the menu.         

        if choice == "0":
            book_id = getInt("Enter EBook ID: ")
            title = input("Enter EBook Title: ")
            author = input("Enter EBook Author: ")
            file_size = getInt("Enter File Size (MB): ")
            library.add_book(Ebook(book_id, title, author, file_size))
        elif choice == "1":
            book_id = getInt("Enter Book ID: ")
            title = input("Enter Book Title: ")
            author = input("Enter Book Author: ")
            copies = getInt("Enter Number of Copies: ")
            library.add_book(Book(book_id, title, author, copies))
        elif choice == "2":
            member_id = getInt("Enter Member ID: ")
            name = input("Enter Member Name: ")
            library.add_member(Member(member_id, name))
        elif choice == "3":
            library.display_books()
        elif choice == "4":
            library.display_members()
        elif choice == "5":
            member_id = getInt("Enter Member ID: ")
            book_id = getInt("Enter Book ID: ")
            library.issue_book(member_id, book_id)
        elif choice == "6":
            member_id = getInt("Enter Member ID: ")
            book_id = getInt("Enter Book ID: ")
            library.return_book(member_id, book_id)
        elif choice == "7":
            library.display_transaction_history()
        elif choice == "8":
            member_id = getInt("Enter Member ID: ")
            library.remove_member(member_id)
        elif choice == "9":
            member_id = getInt("Enter Member ID: ")
            new_name = input("Input The Rename: ")
            library.update_member(member_id, new_name)
        elif choice == "10":
            book_id = getInt("Enter The ID Of The Book You Want To update: ")
            title = input("Enter New Book Title: ")
            author = input("Enter Book Author: ")
            copies = getInt("Enter Number of Copies: ")
            library.update_book(book_id, title, author, copies)
        elif choice == "11":
            search_term = input("Search For Book: ")
            library.search_books(search_term)
        elif choice == "12":
            book_id = getInt("Enter The ID Of The Book You Want To Remove: ")
            library.remove_book(book_id)
        elif choice == "13":
            print("Exiting Library Management System.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":  # Ensures that the main function is called when the script is run directly.
    main()                  # Calls the main function to start the library management system.

'''
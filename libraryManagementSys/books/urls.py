from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

auth_patterns = [
    path('register/', views.register, name='register'),
]

urlpatterns = [
    path('', views.home, name='home'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('add_book/', views.add_book, name='add_book'),
    path('borrow_book/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return_book/<int:book_id>/', views.return_book, name='return_book'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include((auth_patterns, 'registration'))),
    path('my-borrowed-books/', views.my_borrowed_books, name='my_borrowed_books'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:book_id>/', views.return_book, name='return_book'),
    path('reserve/<int:book_id>/', views.reserve_book, name='reserve_book'),
    path('edit_book/<int:book_id>/', views.edit_book, name='edit_book'),  # Behold kun én linje for edit_book
    path('delete_book/<int:book_id>/', views.delete_book, name='delete_book'),
    path('view_borrowing_records/', views.view_borrowing_records, name='view_borrowing_records'),
    path('manage_books/', views.manage_books, name='manage_books'),
    path('edit_books/', views.edit_books, name='edit_books'),
    path('cancel_reservation/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('search/', views.search_books, name='search_books'),
    path('return/<int:book_id>/', views.return_book, name='return_book'),
    path('view_members/', views.view_members, name='view_members'),
    path('edit_member/<int:member_id>/', views.edit_member, name='edit_member'),
]
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name="dashboard"),

    # Books
    path('books/', views.admin, name='admin'),
    path('books/add/', views.add_book, name="add_book"),
    path('books/update/<int:id>/', views.update, name="update"),
    path('books/delete/<int:id>/', views.delete_book, name="delete_book"),

    # Members
    path('members/', views.members, name="members"),
    path('members/add/', views.add_member, name="add_member"),
    path('members/edit/<int:id>/', views.edit_member, name="edit_member"),
    path('members/delete/<int:id>/', views.delete_member, name="delete_member"),

    # Transactions
    path('transactions/', views.transactions, name="transactions"),
    path('transactions/issue/', views.issue_book, name="issue_book"),
    path('transactions/return/<int:id>/', views.return_book, name="admin_return_book"),
    path('transactions/delete/<int:id>/', views.delete_transaction, name="delete_transaction"),
    
    # Book Requests
    path('book-requests/', views.book_requests, name="book_requests"),
    path('book-requests/approve/<int:id>/', views.approve_request, name="approve_request"),
    path('book-requests/reject/<int:id>/', views.reject_request, name="reject_request"),
    path('book-requests/delete/<int:id>/', views.delete_request, name="delete_request")
]

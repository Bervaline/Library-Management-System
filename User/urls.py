from django.urls import path
from . import views

urlpatterns = [
    # Home and browsing
    path('', views.home, name='user_home'),
    path('book/<int:id>/', views.book_detail, name='book_detail'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    
    # User features
    path('my-books/', views.my_books, name='my_books'),
    path('my-transactions/', views.my_transactions, name='my_transactions'),
    path('request-book/<int:id>/', views.request_book, name='request_book'),
    path('return-book/<int:id>/', views.return_book, name='return_book'),
    path('profile/', views.profile, name='profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    
    # Chatbot
    path('chatbot/', views.chatbot, name='chatbot'),
    path('chatbot/query/', views.chatbot_query, name='chatbot_query'),
]

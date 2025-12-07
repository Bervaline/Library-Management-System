from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse
import json

from Admin.models import Book, Member, Transaction, BookRequest
from .chatbot import BookRecommendationChatbot
from .utils import get_or_create_member


def home(request):
    """User home page - Browse all books"""
    search_query = request.GET.get('search', '')
    books = Book.objects.all()
    
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    context = {
        'books': books,
        'search_query': search_query,
    }
    return render(request, 'user/home.html', context)


def book_detail(request, id):
    """View book details"""
    book = get_object_or_404(Book, id=id)
    
    # Check if user has this book issued
    user_has_book = False
    user_transaction = None
    pending_request = None
    
    if request.user.is_authenticated:
        member = get_or_create_member(request.user)
        user_transaction = Transaction.objects.filter(
            member=member,
            book=book,
            status='Issued'
        ).first()
        user_has_book = user_transaction is not None
        
        # Check for pending request
        pending_request = BookRequest.objects.filter(
            member=member,
            book=book,
            status='Pending'
        ).first()
    
    context = {
        'book': book,
        'user_has_book': user_has_book,
        'user_transaction': user_transaction,
        'pending_request': pending_request,
    }
    return render(request, 'user/book_detail.html', context)


def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('user_home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address', '')
        
        # Validation
        if password != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('register')
        
        if Member.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered as a member!')
            return redirect('register')
        
        try:
            # Create User
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=full_name.split()[0] if full_name else '',
                last_name=' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
            )
            
            # Create Member linked to User
            Member.objects.create(
                user=user,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address
            )
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('user_login')
        except Exception as e:
            messages.error(request, f'Error during registration: {str(e)}')
    
    return render(request, 'user/register.html')


def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('user_home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'user_home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'user/login.html')


@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('user_home')


@login_required
def my_books(request):
    """View user's issued books"""
    member = get_or_create_member(request.user, request)
    transactions = Transaction.objects.filter(
        member=member,
        status='Issued'
    ).order_by('-issue_date')
    
    context = {
        'transactions': transactions,
        'member': member,
    }
    
    return render(request, 'user/my_books.html', context)


@login_required
def my_requests(request):
    """View user's book requests"""
    member = get_or_create_member(request.user, request)
    requests = BookRequest.objects.filter(
        member=member
    ).order_by('-request_date')
    
    context = {
        'requests': requests,
        'member': member,
    }
    
    return render(request, 'user/my_requests.html', context)


@login_required
def my_transactions(request):
    """View all user's transactions (issued and returned)"""
    member = get_or_create_member(request.user)
    transactions = Transaction.objects.filter(
        member=member
    ).order_by('-issue_date')
    
    context = {
        'transactions': transactions,
        'member': member,
    }
    
    return render(request, 'user/my_transactions.html', context)


@login_required
def request_book(request, id):
    """Request a book (creates pending request)"""
    book = get_object_or_404(Book, id=id)
    member = get_or_create_member(request.user, request)
    
    # Check if book is available
    if book.available_copies <= 0:
        messages.error(request, 'Sorry, this book is currently not available!')
        return redirect('book_detail', id=id)
    
    # Check if user already has this book issued
    existing_transaction = Transaction.objects.filter(
        member=member,
        book=book,
        status='Issued'
    ).first()
    
    if existing_transaction:
        messages.warning(request, 'You have already issued this book!')
        return redirect('book_detail', id=id)
    
    # Check if user already has a pending request for this book
    existing_request = BookRequest.objects.filter(
        member=member,
        book=book,
        status='Pending'
    ).first()
    
    if existing_request:
        messages.info(request, 'You already have a pending request for this book. Please wait for admin approval.')
        return redirect('book_detail', id=id)
    
    # Create book request (pending)
    try:
        BookRequest.objects.create(
            member=member,
            book=book,
            status='Pending'
        )
        messages.success(request, f'Book request for "{book.title}" submitted successfully! It is now pending admin approval.')
        return redirect('my_requests')
    except Exception as e:
        messages.error(request, f'Error submitting request: {str(e)}')
        return redirect('book_detail', id=id)


@login_required
def return_book(request, id):
    """Return a book"""
    transaction = get_object_or_404(Transaction, id=id)
    member = get_or_create_member(request.user)
    
    # Verify the transaction belongs to the user
    if transaction.member != member:
        messages.error(request, 'You are not authorized to return this book!')
        return redirect('my_books')
    
    if transaction.status == 'Issued':
        transaction.mark_returned()
        messages.success(request, f'Book "{transaction.book.title}" returned successfully!')
    else:
        messages.warning(request, 'This book has already been returned.')
    
    return redirect('my_books')


@login_required
def profile(request):
    """User profile page"""
    member = get_or_create_member(request.user, request)
    
    # Statistics
    issued_count = Transaction.objects.filter(member=member, status='Issued').count()
    returned_count = Transaction.objects.filter(member=member, status='Returned').count()
    total_transactions = Transaction.objects.filter(member=member).count()
    
    context = {
        'member': member,
        'user': request.user,
        'issued_count': issued_count,
        'returned_count': returned_count,
        'total_transactions': total_transactions,
    }
    
    return render(request, 'user/profile.html', context)


@login_required
def update_profile(request):
    """Update user profile"""
    member = get_or_create_member(request.user)
    
    if request.method == 'POST':
        try:
            # Update User
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()
            
            # Update Member
            member.full_name = request.POST.get('full_name', '')
            member.email = request.POST.get('email', '')
            member.phone = request.POST.get('phone', '')
            member.address = request.POST.get('address', '')
            member.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    context = {
        'member': member,
        'user': request.user,
    }
    return render(request, 'user/update_profile.html', context)


def chatbot(request):
    """Book recommendation chatbot page"""
    return render(request, 'user/chatbot.html')


def chatbot_query(request):
    """Handle chatbot queries via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '').strip()
            
            if not query:
                return JsonResponse({
                    'success': False,
                    'message': 'Please enter a query.',
                    'books': []
                })
            
            # Initialize chatbot
            chatbot = BookRecommendationChatbot(user=request.user)
            
            # Process query
            result = chatbot.process_query(query)
            
            # Format response
            response_data = {
                'success': True,
                'type': result.get('type', 'general'),
                'message': result.get('message', ''),
                'books': []
            }
            
            # Format books for JSON response
            for book in result.get('books', []):
                response_data['books'].append({
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'category': book.category,
                    'available_copies': book.available_copies,
                    'image_url': book.image.url if book.image else None,
                    'description': book.description or '',
                })
            
            # Add reference book if exists
            if 'reference_book' in result:
                ref_book = result['reference_book']
                response_data['reference_book'] = {
                    'id': ref_book.id,
                    'title': ref_book.title,
                    'author': ref_book.author,
                    'category': ref_book.category,
                }
            
            # Add category if exists
            if 'category' in result:
                response_data['category'] = result['category']
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error processing query: {str(e)}',
                'books': []
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.',
        'books': []
    })

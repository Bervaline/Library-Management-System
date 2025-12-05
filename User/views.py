from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User

from Admin.models import Book, Member, Transaction


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
    if request.user.is_authenticated:
        try:
            member = Member.objects.get(user=request.user)
            user_transaction = Transaction.objects.filter(
                member=member,
                book=book,
                status='Issued'
            ).first()
            user_has_book = user_transaction is not None
        except Member.DoesNotExist:
            pass
    
    context = {
        'book': book,
        'user_has_book': user_has_book,
        'user_transaction': user_transaction,
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
    try:
        member = Member.objects.get(user=request.user)
        transactions = Transaction.objects.filter(
            member=member,
            status='Issued'
        ).order_by('-issue_date')
        
        context = {
            'transactions': transactions,
            'member': member,
        }
    except Member.DoesNotExist:
        messages.warning(request, 'Member profile not found. Please contact admin.')
        return redirect('user_home')
    
    return render(request, 'user/my_books.html', context)


@login_required
def my_transactions(request):
    """View all user's transactions (issued and returned)"""
    try:
        member = Member.objects.get(user=request.user)
        transactions = Transaction.objects.filter(
            member=member
        ).order_by('-issue_date')
        
        context = {
            'transactions': transactions,
            'member': member,
        }
    except Member.DoesNotExist:
        messages.warning(request, 'Member profile not found. Please contact admin.')
        return redirect('user_home')
    
    return render(request, 'user/my_transactions.html', context)


@login_required
def request_book(request, id):
    """Request/Issue a book"""
    book = get_object_or_404(Book, id=id)
    
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found. Please contact admin.')
        return redirect('user_home')
    
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
    
    # Create transaction
    try:
        Transaction.objects.create(
            member=member,
            book=book,
            status='Issued'
        )
        messages.success(request, f'Book "{book.title}" issued successfully!')
        return redirect('my_books')
    except Exception as e:
        messages.error(request, f'Error issuing book: {str(e)}')
        return redirect('book_detail', id=id)


@login_required
def return_book(request, id):
    """Return a book"""
    transaction = get_object_or_404(Transaction, id=id)
    
    # Verify the transaction belongs to the user
    try:
        member = Member.objects.get(user=request.user)
        if transaction.member != member:
            messages.error(request, 'You are not authorized to return this book!')
            return redirect('my_books')
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found.')
        return redirect('user_home')
    
    if transaction.status == 'Issued':
        transaction.mark_returned()
        messages.success(request, f'Book "{transaction.book.title}" returned successfully!')
    else:
        messages.warning(request, 'This book has already been returned.')
    
    return redirect('my_books')


@login_required
def profile(request):
    """User profile page"""
    try:
        member = Member.objects.get(user=request.user)
        
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
    except Member.DoesNotExist:
        messages.warning(request, 'Member profile not found.')
        return redirect('user_home')
    
    return render(request, 'user/profile.html', context)


@login_required
def update_profile(request):
    """Update user profile"""
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found.')
        return redirect('user_home')
    
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

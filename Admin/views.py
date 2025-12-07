from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Q

from Admin.models import Book, Member, Transaction, BookRequest

# Create your views here.
def admin(request):
    search_query = request.GET.get('search', '')
    books = Book.objects.all()
    
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    return render(request, 'admin.html', {'books': books, 'search_query': search_query})
  

def add_book(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            author = request.POST.get('author')
            isbn = request.POST.get('isbn')
            published_date = request.POST.get('published_date')
            available_copies = request.POST.get('available_copies')
            category = request.POST.get('category', 'Other')
            description = request.POST.get('description', '')
            image = request.FILES.get('image')

            Book.objects.create(
                title=title,
                author=author,
                isbn=isbn,
                published_date=published_date,
                available_copies=available_copies,
                category=category,
                description=description,
                image=image
            )
            messages.success(request, 'Book added successfully!')
            return redirect('admin')
        except Exception as e:
            messages.error(request, f'Error adding book: {str(e)}')

    return render(request, 'add_book.html')

def delete_book(request, id):
    book = get_object_or_404(Book, id=id)
    book.delete()
    messages.success(request, 'Book deleted successfully!')
    return redirect('admin')  

    
def update(request, id):
    book = get_object_or_404(Book, id=id)

    if request.method == 'POST':
        try:
            book.title = request.POST.get('title')
            book.author = request.POST.get('author')
            book.isbn = request.POST.get('isbn')
            book.published_date = request.POST.get('published_date')
            book.available_copies = request.POST.get('available_copies')
            book.category = request.POST.get('category', 'Other')
            book.description = request.POST.get('description', '')
            if 'image' in request.FILES:
                book.image = request.FILES.get('image')
            book.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('admin')
        except Exception as e:
            messages.error(request, f'Error updating book: {str(e)}')

    return render(request, 'update.html', {'book': book})

def dashboard(request):
    total_books = Book.objects.count()
    total_members = Member.objects.count()
    issued_books = Transaction.objects.filter(status="Issued").count()
    returned_books = Transaction.objects.filter(status="Returned").count()
    total_transactions = Transaction.objects.count()
    pending_requests = BookRequest.objects.filter(status="Pending").count()
    
    # Calculate return rate
    return_rate = 0
    if total_transactions > 0:
        return_rate = (returned_books / total_transactions) * 100
    
    # Recent transactions
    recent_transactions = Transaction.objects.all().order_by('-issue_date')[:5]
    
    # Recent pending requests
    recent_requests = BookRequest.objects.filter(status="Pending").order_by('-request_date')[:5]
    
    # Books with low stock (less than 5 copies)
    low_stock_books = Book.objects.filter(available_copies__lt=5).count()

    context = {
        'total_books': total_books,
        'total_members': total_members,
        'issued_books': issued_books,
        'returned_books': returned_books,
        'total_transactions': total_transactions,
        'recent_transactions': recent_transactions,
        'low_stock_books': low_stock_books,
        'return_rate': return_rate,
        'pending_requests': pending_requests,
        'recent_requests': recent_requests,
    }
    return render(request, 'dashboard.html', context)


def members(request):
    search_query = request.GET.get('search', '')
    all_members = Member.objects.all()
    
    if search_query:
        all_members = all_members.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    return render(request, 'members.html', {'members': all_members, 'search_query': search_query})



def edit_member(request, id):
    member = get_object_or_404(Member, id=id)

    if request.method == "POST":
        try:
            member.full_name = request.POST['full_name']
            member.email = request.POST['email']
            member.phone = request.POST['phone']
            member.address = request.POST['address']
            member.save()
            messages.success(request, 'Member updated successfully!')
            return redirect('members')
        except Exception as e:
            messages.error(request, f'Error updating member: {str(e)}')

    return render(request, 'edit_member.html', {'member': member})

def add_member(request):
    if request.method == "POST":
        try:
            Member.objects.create(
                full_name=request.POST['full_name'],
                email=request.POST['email'],
                phone=request.POST['phone'],
                address=request.POST['address']
            )
            messages.success(request, 'Member added successfully!')
            return redirect('members')
        except Exception as e:
            messages.error(request, f'Error adding member: {str(e)}')

    return render(request, 'add_member.html')

def delete_member(request, id):
    member = get_object_or_404(Member, id=id)
    member.delete()
    messages.success(request, 'Member deleted successfully!')
    return redirect('members')

def issue_book(request):
    members = Member.objects.all()
    books = Book.objects.filter(available_copies__gt=0)

    if request.method == "POST":
        try:
            member_id = request.POST['member']
            book_id = request.POST['book']

            book = Book.objects.get(id=book_id)
            member = Member.objects.get(id=member_id)

            if book.available_copies <= 0:
                messages.error(request, 'No copies available for this book!')
                return redirect('issue_book')

            # Create transaction - the model's save method will handle copy reduction
            Transaction.objects.create(
                member=member,
                book=book,
                status="Issued"
            )

            messages.success(request, f'Book "{book.title}" issued to {member.full_name} successfully!')
            return redirect('transactions')
        except Exception as e:
            messages.error(request, f'Error issuing book: {str(e)}')

    return render(request, 'issue_book.html', {'members': members, 'books': books})


def transactions(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    all_transactions = Transaction.objects.all().order_by('-issue_date')
    
    if search_query:
        all_transactions = all_transactions.filter(
            Q(member__full_name__icontains=search_query) |
            Q(book__title__icontains=search_query) |
            Q(book__author__icontains=search_query)
        )
    
    if status_filter:
        all_transactions = all_transactions.filter(status=status_filter)
    
    return render(request, 'transactions.html', {
        'transactions': all_transactions,
        'search_query': search_query,
        'status_filter': status_filter
    })

def return_book(request, id):
    t = get_object_or_404(Transaction, id=id)

    if t.status == "Issued":
        # Use the model's mark_returned method which handles everything
        t.mark_returned()
        messages.success(request, f'Book "{t.book.title}" returned successfully!')
    else:
        messages.warning(request, 'This book has already been returned.')

    return redirect('transactions')


def delete_transaction(request, id):
    t = get_object_or_404(Transaction, id=id)
    
    # If transaction is issued, restore the book copy
    if t.status == "Issued":
        t.book.available_copies += 1
        t.book.save()
    
    t.delete()
    messages.success(request, 'Transaction deleted successfully!')
    return redirect('transactions')


def book_requests(request):
    """View all book requests"""
    status_filter = request.GET.get('status', 'Pending')
    
    requests = BookRequest.objects.all().order_by('-request_date')
    
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    context = {
        'requests': requests,
        'status_filter': status_filter,
        'pending_count': BookRequest.objects.filter(status='Pending').count(),
    }
    return render(request, 'book_requests.html', context)


def approve_request(request, id):
    """Approve a book request and create transaction"""
    book_request = get_object_or_404(BookRequest, id=id)
    
    if book_request.status != 'Pending':
        messages.warning(request, 'This request has already been processed.')
        return redirect('book_requests')
    
    # Check if book is still available
    if book_request.book.available_copies <= 0:
        messages.error(request, 'Book is no longer available. Cannot approve request.')
        book_request.status = 'Rejected'
        book_request.admin_notes = 'Book no longer available'
        book_request.save()
        return redirect('book_requests')
    
    # Check if member already has this book issued
    existing_transaction = Transaction.objects.filter(
        member=book_request.member,
        book=book_request.book,
        status='Issued'
    ).first()
    
    if existing_transaction:
        messages.warning(request, 'Member already has this book issued.')
        book_request.status = 'Rejected'
        book_request.admin_notes = 'Member already has this book issued'
        book_request.save()
        return redirect('book_requests')
    
    try:
        # Create transaction
        transaction = Transaction.objects.create(
            member=book_request.member,
            book=book_request.book,
            status='Issued',
            book_request=book_request
        )
        
        # Update request status
        book_request.status = 'Approved'
        book_request.save()
        
        messages.success(request, f'Request approved! Book "{book_request.book.title}" issued to {book_request.member.full_name}.')
    except Exception as e:
        messages.error(request, f'Error approving request: {str(e)}')
    
    return redirect('book_requests')


def reject_request(request, id):
    """Reject a book request"""
    book_request = get_object_or_404(BookRequest, id=id)
    
    if book_request.status != 'Pending':
        messages.warning(request, 'This request has already been processed.')
        return redirect('book_requests')
    
    if request.method == 'POST':
        admin_notes = request.POST.get('admin_notes', '')
        book_request.status = 'Rejected'
        book_request.admin_notes = admin_notes
        book_request.save()
        messages.success(request, 'Request rejected successfully.')
        return redirect('book_requests')
    
    return render(request, 'reject_request.html', {'book_request': book_request})


def delete_request(request, id):
    """Delete a book request"""
    book_request = get_object_or_404(BookRequest, id=id)
    book_request.delete()
    messages.success(request, 'Request deleted successfully!')
    return redirect('book_requests')



from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True)
    date_joined = models.DateField(default=timezone.now)

    def __str__(self):
        return self.full_name
    
# Create your models here.
class Book(models.Model):
    CATEGORY_CHOICES = (
        ('Fiction', 'Fiction'),
        ('Non-Fiction', 'Non-Fiction'),
        ('Science Fiction', 'Science Fiction'),
        ('Fantasy', 'Fantasy'),
        ('Mystery', 'Mystery'),
        ('Romance', 'Romance'),
        ('History', 'History'),
        ('Biography', 'Biography'),
        ('Science', 'Science'),
        ('Technology', 'Technology'),
        ('Programming', 'Programming'),
        ('Business', 'Business'),
        ('Education', 'Education'),
        ('Philosophy', 'Philosophy'),
        ('Literature', 'Literature'),
        ('Other', 'Other'),
    )
    
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    published_date = models.DateField()
    available_copies = models.IntegerField(default=0)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    description = models.TextField(blank=True, null=True, help_text="Brief description of the book")
    
    image = models.ImageField(upload_to='book_images/', blank=True, null=True)

    def __str__(self):
        return self.title
    
    


class BookRequest(models.Model):
    """Model to track book requests from users"""
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    admin_notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-request_date']

    def __str__(self):
        return f"{self.member.full_name} - {self.book.title} ({self.status})"


class Transaction(models.Model):
    STATUS_CHOICES = (
        ('Issued', 'Issued'),
        ('Returned', 'Returned'),
    )

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    book_request = models.OneToOneField(BookRequest, on_delete=models.SET_NULL, null=True, blank=True)

    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Issued')

    def __str__(self):
        return f"{self.member.full_name} - {self.book.title}"

    # Auto-update counts on save
    def save(self, *args, **kwargs):
        if not self.id:  # New transaction → Issue book
            self.book.available_copies -= 1
            self.book.save()
        super().save(*args, **kwargs)

    def mark_returned(self):
        """Call this when returning a book."""
        if self.status == 'Issued':
            self.status = 'Returned'
            self.return_date = timezone.now().date()
            self.book.available_copies += 1
            self.book.save()
            self.save()

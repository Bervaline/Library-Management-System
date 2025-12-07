from django.contrib import admin
from Admin.models import Book, Member, Transaction, BookRequest


# Register your models here.
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'available_copies', 'published_date')
    list_filter = ('published_date',)
    search_fields = ('title', 'author', 'isbn')

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'date_joined')
    list_filter = ('date_joined',)
    search_fields = ('full_name', 'email', 'phone')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('member', 'book', 'issue_date', 'return_date', 'status')
    list_filter = ('status', 'issue_date')
    search_fields = ('member__full_name', 'book__title')
    date_hierarchy = 'issue_date'

@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ('member', 'book', 'request_date', 'status')
    list_filter = ('status', 'request_date')
    search_fields = ('member__full_name', 'book__title')
    date_hierarchy = 'request_date'
"""
Smart Book Recommendation Chatbot
Handles various types of book recommendation queries
"""
from django.db.models import Q, Count
from Admin.models import Book, Transaction, Member


class BookRecommendationChatbot:
    """Chatbot for book recommendations"""
    
    def __init__(self, user=None):
        self.user = user
        self.member = None
        if user and user.is_authenticated:
            try:
                self.member = Member.objects.get(user=user)
            except Member.DoesNotExist:
                pass
    
    def process_query(self, query):
        """Process user query and return recommendations"""
        query_lower = query.lower().strip()
        
        # Similar book recommendations
        if any(keyword in query_lower for keyword in ['similar', 'like', 'same as', 'recommend like']):
            return self._find_similar_books(query)
        
        # Most borrowed books by category
        elif any(keyword in query_lower for keyword in ['most borrowed', 'popular', 'top', 'best']):
            return self._find_most_borrowed_by_category(query)
        
        # Beginner recommendations
        elif any(keyword in query_lower for keyword in ['beginner', 'start', 'learn', 'introduction', 'intro']):
            return self._find_beginner_books(query)
        
        # Personalized recommendations
        elif any(keyword in query_lower for keyword in ['recommend', 'suggest', 'what should', 'what can']):
            if self.member:
                return self._personalized_recommendations(query)
            else:
                return self._general_recommendations(query)
        
        # Category-based search
        elif any(category.lower() in query_lower for category in [cat[0] for cat in Book.CATEGORY_CHOICES]):
            return self._find_by_category(query)
        
        # Author search
        elif 'author' in query_lower or 'by' in query_lower:
            return self._find_by_author(query)
        
        # Default: search by title/keywords
        else:
            return self._search_books(query)
    
    def _find_similar_books(self, query):
        """Find books similar to a given book"""
        # Extract book title from query
        query_words = query.lower().split()
        
        # Remove common words
        stop_words = ['similar', 'to', 'like', 'same', 'as', 'recommend', 'suggest', 'book', 'books']
        keywords = [word for word in query_words if word not in stop_words]
        
        if not keywords:
            return {
                'type': 'error',
                'message': "I couldn't find the book you're looking for. Please mention a book title.",
                'books': []
            }
        
        # Find the book user is referring to
        book_query = Q()
        for keyword in keywords:
            book_query |= Q(title__icontains=keyword) | Q(author__icontains=keyword)
        
        reference_book = Book.objects.filter(book_query).first()
        
        if not reference_book:
            return {
                'type': 'error',
                'message': f"I couldn't find a book matching '{' '.join(keywords)}' in our library.",
                'books': []
            }
        
        # Find similar books (same category, same author, or similar title)
        similar_books = Book.objects.filter(
            Q(category=reference_book.category) |
            Q(author=reference_book.author) |
            Q(title__icontains=keywords[0])
        ).exclude(id=reference_book.id).filter(available_copies__gt=0)[:5]
        
        if similar_books.exists():
            return {
                'type': 'similar',
                'message': f"Here are books similar to '{reference_book.title}' by {reference_book.author}:",
                'reference_book': reference_book,
                'books': list(similar_books)
            }
        else:
            return {
                'type': 'similar',
                'message': f"I found '{reference_book.title}' but couldn't find similar books. Here are some available books:",
                'reference_book': reference_book,
                'books': list(Book.objects.filter(available_copies__gt=0).exclude(id=reference_book.id)[:5])
            }
    
    def _find_most_borrowed_by_category(self, query):
        """Find most borrowed books in a category"""
        query_lower = query.lower()
        
        # Extract category from query
        category = None
        for cat_choice in Book.CATEGORY_CHOICES:
            if cat_choice[0].lower() in query_lower or cat_choice[1].lower() in query_lower:
                category = cat_choice[0]
                break
        
        if not category:
            # Try to infer category from keywords
            category_mapping = {
                'history': 'History',
                'programming': 'Programming',
                'tech': 'Technology',
                'science': 'Science',
                'fiction': 'Fiction',
                'fantasy': 'Fantasy',
                'mystery': 'Mystery',
                'romance': 'Romance',
            }
            for key, cat in category_mapping.items():
                if key in query_lower:
                    category = cat
                    break
        
        if category:
            # Get most borrowed books in this category
            books = Book.objects.filter(category=category).annotate(
                borrow_count=Count('transaction')
            ).order_by('-borrow_count', '-available_copies')[:5]
            
            if books.exists():
                return {
                    'type': 'category',
                    'message': f"Here are the most borrowed books in the {category} category:",
                    'category': category,
                    'books': list(books)
                }
        
        # If no category found or no books, return general most borrowed
        books = Book.objects.annotate(
            borrow_count=Count('transaction')
        ).order_by('-borrow_count', '-available_copies')[:5]
        
        return {
            'type': 'category',
            'message': "Here are the most borrowed books in our library:",
            'category': 'All Categories',
            'books': list(books)
        }
    
    def _find_beginner_books(self, query):
        """Find beginner-friendly books"""
        query_lower = query.lower()
        
        # Extract topic/category
        topic = None
        for cat_choice in Book.CATEGORY_CHOICES:
            if cat_choice[0].lower() in query_lower:
                topic = cat_choice[0]
                break
        
        # Common beginner keywords
        beginner_keywords = ['introduction', 'beginner', 'basics', 'fundamentals', 'getting started', 'learn']
        
        if topic:
            # Search for beginner books in that topic
            books = Book.objects.filter(
                Q(category=topic) &
                (Q(title__icontains='introduction') |
                 Q(title__icontains='beginner') |
                 Q(title__icontains='basics') |
                 Q(title__icontains='fundamentals') |
                 Q(description__icontains='beginner') |
                 Q(description__icontains='introduction'))
            ).filter(available_copies__gt=0)[:5]
            
            if not books.exists():
                # Fallback to any books in that category
                books = Book.objects.filter(category=topic, available_copies__gt=0)[:5]
        else:
            # General beginner books
            books = Book.objects.filter(
                Q(title__icontains='introduction') |
                Q(title__icontains='beginner') |
                Q(title__icontains='basics') |
                Q(description__icontains='beginner')
            ).filter(available_copies__gt=0)[:5]
        
        if books.exists():
            topic_text = f" for {topic}" if topic else ""
            return {
                'type': 'beginner',
                'message': f"Here are some beginner-friendly books{topic_text}:",
                'books': list(books)
            }
        else:
            return {
                'type': 'beginner',
                'message': "I couldn't find specific beginner books. Here are some available books:",
                'books': list(Book.objects.filter(available_copies__gt=0)[:5])
            }
    
    def _personalized_recommendations(self, query):
        """Provide personalized recommendations based on user's borrowing history"""
        if not self.member:
            return self._general_recommendations(query)
        
        # Get user's borrowing history
        user_transactions = Transaction.objects.filter(member=self.member)
        
        if not user_transactions.exists():
            return {
                'type': 'personalized',
                'message': "You haven't borrowed any books yet. Here are some popular recommendations to get you started:",
                'books': list(Book.objects.annotate(
                    borrow_count=Count('transaction')
                ).order_by('-borrow_count', '-available_copies').filter(available_copies__gt=0)[:5])
            }
        
        # Get categories of books user has borrowed
        borrowed_categories = set()
        borrowed_authors = set()
        for transaction in user_transactions:
            borrowed_categories.add(transaction.book.category)
            borrowed_authors.add(transaction.book.author)
        
        # Recommend books in similar categories or by same authors
        recommendations = Book.objects.filter(
            Q(category__in=borrowed_categories) |
            Q(author__in=borrowed_authors)
        ).exclude(
            id__in=[t.book.id for t in user_transactions.filter(status='Issued')]
        ).filter(available_copies__gt=0).distinct()[:5]
        
        if recommendations.exists():
            return {
                'type': 'personalized',
                'message': "Based on your reading history, here are some personalized recommendations:",
                'books': list(recommendations)
            }
        else:
            # Fallback to popular books
            return {
                'type': 'personalized',
                'message': "Based on your preferences, here are some popular books you might like:",
                'books': list(Book.objects.annotate(
                    borrow_count=Count('transaction')
                ).order_by('-borrow_count', '-available_copies').filter(available_copies__gt=0)[:5])
            }
    
    def _general_recommendations(self, query):
        """Provide general recommendations"""
        books = Book.objects.annotate(
            borrow_count=Count('transaction')
        ).order_by('-borrow_count', '-available_copies').filter(available_copies__gt=0)[:5]
        
        return {
            'type': 'general',
            'message': "Here are some popular book recommendations:",
            'books': list(books)
        }
    
    def _find_by_category(self, query):
        """Find books by category"""
        query_lower = query.lower()
        
        category = None
        for cat_choice in Book.CATEGORY_CHOICES:
            if cat_choice[0].lower() in query_lower:
                category = cat_choice[0]
                break
        
        if category:
            books = Book.objects.filter(category=category, available_copies__gt=0)[:10]
            return {
                'type': 'category',
                'message': f"Here are available books in the {category} category:",
                'category': category,
                'books': list(books)
            }
        
        return {
            'type': 'error',
            'message': "I couldn't identify the category. Please try again.",
            'books': []
        }
    
    def _find_by_author(self, query):
        """Find books by author"""
        # Extract author name
        query_words = query.lower().split()
        stop_words = ['author', 'by', 'books', 'book', 'from']
        keywords = [word for word in query_words if word not in stop_words]
        
        if keywords:
            author_query = Q()
            for keyword in keywords:
                author_query |= Q(author__icontains=keyword)
            
            books = Book.objects.filter(author_query, available_copies__gt=0)[:10]
            
            if books.exists():
                return {
                    'type': 'author',
                    'message': f"Here are books by authors matching '{' '.join(keywords)}':",
                    'books': list(books)
                }
        
        return {
            'type': 'error',
            'message': "I couldn't find books by that author. Please try again.",
            'books': []
        }
    
    def _search_books(self, query):
        """General book search"""
        query_words = query.lower().split()
        
        book_query = Q()
        for word in query_words:
            book_query |= Q(title__icontains=word) | Q(author__icontains=word) | Q(category__icontains=word)
        
        books = Book.objects.filter(book_query, available_copies__gt=0)[:10]
        
        if books.exists():
            return {
                'type': 'search',
                'message': f"Here are books matching '{query}':",
                'books': list(books)
            }
        
        return {
            'type': 'error',
            'message': f"I couldn't find any books matching '{query}'. Try a different search term.",
            'books': []
        }


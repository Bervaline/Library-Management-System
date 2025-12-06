# Library Management System (LMS)

A comprehensive web-based Library Management System built with Django, featuring separate admin and user interfaces for managing books, members, and transactions.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Setup Instructions](#setup-instructions)
- [Usage Guide](#usage-guide)
- [URL Structure](#url-structure)
- [Database Models](#database-models)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This Library Management System provides a complete solution for managing a library's operations. It includes:

- **Admin Panel**: For librarians to manage books, members, and transactions
- **User Portal**: For library members to browse books, request/return books, and view their history
- **Authentication System**: Secure user registration and login
- **Search Functionality**: Search books by title, author, or ISBN
- **Transaction Management**: Track book issues and returns

## ✨ Features

### Admin Features
- 📚 **Book Management**
  - Add, edit, and delete books
  - Upload book cover images
  - Track available copies
  - Search and filter books
  
- 👥 **Member Management**
  - Add, edit, and delete members
  - View member details and history
  - Search members
  
- 📖 **Transaction Management**
  - Issue books to members
  - Mark books as returned
  - View all transactions
  - Filter by status (Issued/Returned)
  - Search transactions
  
- 📊 **Dashboard**
  - View statistics (total books, members, transactions)
  - Monitor issued and returned books
  - Track low stock books
  - View recent transactions

### User Features
- 🔍 **Book Browsing**
  - Browse all available books
  - Search books by title, author, or ISBN
  - View detailed book information
  - See book availability status
  
- 📚 **Book Management**
  - Request/Issue books
  - View issued books
  - Return books
  - View transaction history
  
- 👤 **Profile Management**
  - View profile information
  - Update personal details
  - View statistics (issued books, returned books)

### Security Features
- User authentication and authorization
- CSRF protection
- Password validation
- Session management
- Protected routes with login requirements

## 🛠 Technology Stack

- **Backend**: Django 5.2.9
- **Database**: SQLite (default, can be changed to PostgreSQL/MySQL)
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5.3
- **Icons**: Font Awesome 6.5
- **Python**: 3.13+

## 📁 Project Structure

```
Library-Project/
│
├── LMS/
│   ├── Admin/                    # Admin app
│   │   ├── migrations/           # Database migrations
│   │   ├── templates/           # Admin templates
│   │   │   ├── base.html
│   │   │   ├── dashboard.html
│   │   │   ├── admin.html
│   │   │   ├── add_book.html
│   │   │   ├── update.html
│   │   │   ├── members.html
│   │   │   ├── add_member.html
│   │   │   ├── edit_member.html
│   │   │   ├── transactions.html
│   │   │   └── issue_book.html
│   │   ├── models.py            # Book, Member, Transaction models
│   │   ├── views.py             # Admin views
│   │   ├── urls.py              # Admin URLs
│   │   └── admin.py             # Django admin configuration
│   │
│   ├── User/                     # User app
│   │   ├── templates/
│   │   │   └── user/
│   │   │       ├── base.html
│   │   │       ├── home.html
│   │   │       ├── book_detail.html
│   │   │       ├── login.html
│   │   │       ├── register.html
│   │   │       ├── my_books.html
│   │   │       ├── my_transactions.html
│   │   │       ├── profile.html
│   │   │       └── update_profile.html
│   │   ├── models.py
│   │   ├── views.py             # User views
│   │   └── urls.py              # User URLs
│   │
│   ├── LMS/                      # Project settings
│   │   ├── settings.py          # Django settings
│   │   ├── urls.py              # Main URL configuration
│   │   └── wsgi.py
│   │
│   ├── static/                   # Static files
│   │   ├── css/
│   │   └── bootstrap/
│   │
│   ├── media/                    # Media files (created after first upload)
│   │   └── book_images/
│   │
│   ├── db.sqlite3                # SQLite database
│   └── manage.py                 # Django management script
│
└── README.md                     # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd Library-Project

# Or extract the downloaded ZIP file
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
cd LMS
pip install django pillow
```

**Note**: Pillow is required for image handling. If you encounter issues installing Pillow, you may need to install system dependencies first.

### Step 4: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

This will create the database tables for:
- Django's built-in User model
- Book model
- Member model
- Transaction model

### Step 5: Create Superuser (Optional)

Create a superuser account to access Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### Step 6: Run the Development Server

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

## 📖 Setup Instructions

### Initial Setup

1. **Create Media Directory** (if not exists)
   - The `media/` directory will be created automatically when you upload the first image
   - Or create it manually: `mkdir media` inside the `LMS` folder

2. **Collect Static Files** (if needed)
   ```bash
   python manage.py collectstatic
   ```

3. **Access the Application**
   - User Portal: `http://127.0.0.1:8000/`
   - Admin Panel: `http://127.0.0.1:8000/admin-panel/`
   - Django Admin: `http://127.0.0.1:8000/django-admin/`

### First-Time Admin Setup

1. Access the admin panel at `/admin-panel/`
2. Add books using the "Add New Book" button
3. Add members manually or wait for users to register
4. Start issuing books to members

## 📚 Usage Guide

### For Administrators

#### Accessing Admin Panel
1. Navigate to `http://127.0.0.1:8000/admin-panel/`
2. You'll see the dashboard with statistics

#### Managing Books
1. Click on "Books" in the sidebar or navigate to `/admin-panel/books/`
2. **Add Book**: Click "Add New Book" button
   - Fill in: Title, Author, ISBN, Published Date, Available Copies
   - Optionally upload a book cover image
   - Click "Save Book"
3. **Edit Book**: Click "Edit" button on any book
   - Modify the details
   - Click "Update Book"
4. **Delete Book**: Click "Delete" button (with confirmation)
5. **Search Books**: Use the search bar to find books by title, author, or ISBN

#### Managing Members
1. Click on "Members" in the sidebar
2. **Add Member**: Click "Add Member" button
   - Fill in: Full Name, Email, Phone, Address (optional)
   - Click "Save Member"
3. **Edit Member**: Click "Edit" button
4. **Delete Member**: Click "Delete" button
5. **Search Members**: Use the search bar

#### Managing Transactions
1. Click on "Transactions" in the sidebar
2. **Issue Book**: Click "Issue Book" button
   - Select a member from dropdown
   - Select an available book
   - Click "Issue Book"
3. **Return Book**: Click "Mark Return" button on issued transactions
4. **Filter Transactions**: Use status filter dropdown
5. **Search Transactions**: Search by member name, book title, or author

#### Dashboard Features
- View total books, members, issued books, and returned books
- See low stock alerts (books with less than 5 copies)
- View recent transactions
- Quick action buttons for common tasks

### For Library Members (Users)

#### Registration
1. Navigate to `http://127.0.0.1:8000/` or `/user/register/`
2. Fill in the registration form:
   - Full Name
   - Username (unique)
   - Email (unique)
   - Phone
   - Address (optional)
   - Password and Confirm Password
3. Click "Register"
4. You'll be redirected to login page

#### Login
1. Navigate to `/user/login/`
2. Enter your username and password
3. Click "Login"
4. You'll be redirected to the home page

#### Browsing Books
1. On the home page, you'll see all available books
2. **Search Books**: Use the search bar to find specific books
3. **View Details**: Click "View Details" on any book card
4. See book information, availability, and cover image

#### Requesting/Issuing Books
1. Navigate to a book's detail page
2. If the book is available and you're logged in:
   - Click "Request This Book" button
   - The book will be issued to you
   - You'll see a success message
3. If you already have the book issued:
   - You'll see a message indicating you already have it
   - Link to "My Books" page

#### Managing Your Books
1. Click "My Books" in the navigation (or `/user/my-books/`)
2. View all your currently issued books
3. **Return Book**: Click "Return" button
   - Confirm the return
   - Book will be marked as returned
4. **View Book Details**: Click "View" button

#### Viewing Transaction History
1. Click "My Transactions" in the navigation (or `/user/my-transactions/`)
2. View all your past and current transactions
3. See issue dates, return dates, and status

#### Managing Profile
1. Click on your username in the navigation → "Profile"
2. View your profile information and statistics
3. **Update Profile**: Click "Edit Profile"
   - Modify your details
   - Click "Update Profile"

## 🔗 URL Structure

### User URLs
- `/` or `/user/` - Home page (book browsing)
- `/user/login/` - User login
- `/user/register/` - User registration
- `/user/logout/` - User logout
- `/user/book/<id>/` - Book detail page
- `/user/request-book/<id>/` - Request/Issue a book
- `/user/my-books/` - User's issued books
- `/user/my-transactions/` - Transaction history
- `/user/profile/` - User profile
- `/user/update-profile/` - Edit profile
- `/user/return-book/<id>/` - Return a book

### Admin URLs
- `/admin-panel/` - Admin dashboard
- `/admin-panel/books/` - Books management
- `/admin-panel/books/add/` - Add new book
- `/admin-panel/books/update/<id>/` - Update book
- `/admin-panel/books/delete/<id>/` - Delete book
- `/admin-panel/members/` - Members management
- `/admin-panel/members/add/` - Add new member
- `/admin-panel/members/edit/<id>/` - Edit member
- `/admin-panel/members/delete/<id>/` - Delete member
- `/admin-panel/transactions/` - Transactions management
- `/admin-panel/transactions/issue/` - Issue a book
- `/admin-panel/transactions/return/<id>/` - Return a book
- `/admin-panel/transactions/delete/<id>/` - Delete transaction

### Django Admin
- `/django-admin/` - Django admin interface

## 🗄 Database Models

### Book Model
- `title` - Book title (CharField, max 200)
- `author` - Author name (CharField, max 100)
- `isbn` - ISBN number (CharField, max 13, unique)
- `published_date` - Publication date (DateField)
- `available_copies` - Number of available copies (IntegerField)
- `image` - Book cover image (ImageField, optional)

### Member Model
- `user` - Link to Django User (OneToOneField, optional)
- `full_name` - Full name (CharField, max 200)
- `email` - Email address (EmailField, unique)
- `phone` - Phone number (CharField, max 20)
- `address` - Address (CharField, max 255, optional)
- `date_joined` - Join date (DateField, auto)

### Transaction Model
- `member` - Foreign key to Member
- `book` - Foreign key to Book
- `issue_date` - Issue date (DateField, auto)
- `return_date` - Return date (DateField, optional)
- `status` - Status: 'Issued' or 'Returned' (CharField)

**Note**: When a transaction is created, the book's available copies are automatically decreased. When returned, copies are increased.

## 🔧 Configuration

### Settings File (`LMS/settings.py`)

Key settings you might want to modify:

- **DEBUG**: Set to `False` in production
- **SECRET_KEY**: Change in production
- **ALLOWED_HOSTS**: Add your domain in production
- **DATABASES**: Change from SQLite to PostgreSQL/MySQL for production
- **MEDIA_ROOT**: Media files directory
- **STATIC_URL**: Static files URL

### Login Configuration

- `LOGIN_URL = '/user/login/'` - Redirects unauthenticated users
- `LOGIN_REDIRECT_URL = '/user/'` - Redirects after login
- `LOGOUT_REDIRECT_URL = '/user/'` - Redirects after logout

## 🐛 Troubleshooting

### Common Issues

#### 1. Migration Errors
```bash
# If you get migration errors, try:
python manage.py makemigrations --empty Admin
python manage.py migrate
```

#### 2. Image Upload Issues
- Ensure `Pillow` is installed: `pip install pillow`
- Check that `media/` directory exists and is writable
- Verify `MEDIA_ROOT` and `MEDIA_URL` in settings.py

#### 3. Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic

# Or ensure DEBUG = True in development
```

#### 4. User Registration Issues
- Ensure email is unique
- Check that username doesn't already exist
- Verify password fields match

#### 5. Book Issue Errors
- Ensure book has available copies > 0
- Check that member exists
- Verify user is logged in

#### 6. Template Not Found Errors
- Ensure templates are in correct directories
- Check `TEMPLATES` setting in `settings.py`
- Verify `APP_DIRS = True` in TEMPLATES configuration

### Database Reset

If you need to reset the database:

```bash
# Delete the database file
rm db.sqlite3  # Linux/Mac
del db.sqlite3  # Windows

# Delete migration files (except __init__.py)
# Then recreate migrations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 🔒 Security Considerations

### For Production Deployment

1. **Change SECRET_KEY**: Generate a new secret key
2. **Set DEBUG = False**: Never run with DEBUG=True in production
3. **Configure ALLOWED_HOSTS**: Add your domain
4. **Use HTTPS**: Configure SSL certificates
5. **Database**: Use PostgreSQL or MySQL instead of SQLite
6. **Static Files**: Use a proper web server (Nginx, Apache) or CDN
7. **Media Files**: Store in cloud storage (AWS S3, etc.)
8. **CSRF Protection**: Already enabled, ensure it's working
9. **Password Security**: Django's password validators are enabled
10. **Session Security**: Configure secure session cookies

## 📝 Development Notes

### Adding New Features

1. **New Model**: Add to `Admin/models.py`, run migrations
2. **New View**: Add to `Admin/views.py` or `User/views.py`
3. **New URL**: Add to respective `urls.py` file
4. **New Template**: Create in appropriate `templates/` directory

### Code Structure

- **Models**: Database schema in `Admin/models.py`
- **Views**: Business logic in `Admin/views.py` and `User/views.py`
- **Templates**: HTML templates in respective `templates/` directories
- **URLs**: URL routing in `urls.py` files
- **Static**: CSS, JS, images in `static/` directory
- **Media**: User-uploaded files in `media/` directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Developed as a comprehensive Library Management System using Django.

## 🙏 Acknowledgments

- Django Framework
- Bootstrap for UI components
- Font Awesome for icons
- Python community

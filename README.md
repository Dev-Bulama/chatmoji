# ChatMoji - Django Chat Application

A modern, real-time chat application built with Django where every word gets converted to emojis! Features include user authentication, friend system, WebSocket-based real-time messaging, and a beautiful responsive UI.

## 🚀 Features

- **Real-time messaging** with WebSocket technology
- **Emoji conversion** - Every word automatically converts to emojis
- **Friend system** with requests and online status
- **User authentication** and profile management
- **Responsive design** for all devices
- **Facebook-style chat interface**
- **Typing indicators** and read receipts

## 📁 Project Structure

After running the setup script, your project structure should look like this:

```
chatmoji_project/
├── chatmoji_env/                 # Virtual environment
├── chatmoji_project/            # Main project folder
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                    # User authentication app
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── create_demo_users.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── chat/                        # Chat functionality app
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py
│   ├── models.py
│   ├── routing.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── core/                        # Core app for landing page
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── templates/                   # HTML templates
│   ├── base.html
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   ├── edit_profile.html
│   │   ├── friends_list.html
│   │   └── friend_requests.html
│   ├── chat/
│   │   ├── dashboard.html
│   │   └── conversation.html
│   └── core/
│       └── landing.html
├── static/                      # Static files (CSS, JS, images)
├── media/                       # User uploaded files
├── manage.py
├── requirements.txt
├── setup.bat
└── README.md
```

## 🛠️ Setup Instructions

### Step 1: Run the Setup Script

1. **Download** all the provided files and place them in your project directory
2. **Run the setup script** by double-clicking `setup.bat` or running it from command prompt:
   ```bash
   setup.bat
   ```

This script will:
- Create a virtual environment
- Install all required packages
- Create the Django project structure
- Set up the database
- Create necessary directories

### Step 2: Create and Configure Files

After running the setup script, you need to create/replace the following files with the provided content:

#### Configuration Files
- `chatmoji_project/settings.py` - Replace with provided Django settings
- `chatmoji_project/asgi.py` - Replace with provided ASGI configuration
- `chatmoji_project/urls.py` - Replace with provided URL configuration

#### App Files
Create these files in their respective directories:

**Accounts App (`accounts/`):**
- `models.py` - User models and friendship system
- `views.py` - Authentication and user management views
- `forms.py` - Registration and profile forms
- `urls.py` - Accounts URL patterns
- `admin.py` - Admin interface configuration
- `management/commands/create_demo_users.py` - Demo users command

**Chat App (`chat/`):**
- `models.py` - Chat models for conversations and messages
- `views.py` - Chat views and API endpoints
- `urls.py` - Chat URL patterns
- `consumers.py` - WebSocket consumers for real-time chat
- `routing.py` - WebSocket routing
- `admin.py` - Chat admin configuration

**Core App (`core/`):**
- `views.py` - Landing page view
- `urls.py` - Core URL patterns

#### Templates (`templates/`)
Create all the HTML template files as provided:
- `base.html` - Base template with navigation
- `core/landing.html` - Landing page
- `accounts/login.html` - Login page
- `accounts/register.html` - Registration page
- `accounts/profile.html` - User profile page
- `accounts/edit_profile.html` - Edit profile page
- `accounts/friends_list.html` - Friends list page
- `accounts/friend_requests.html` - Friend requests page
- `chat/dashboard.html` - Chat dashboard
- `chat/conversation.html` - Chat conversation page

### Step 3: Apply Migrations and Create Demo Users

1. **Activate the virtual environment:**
   ```bash
   chatmoji_env\Scripts\activate
   ```

2. **Make and apply migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

4. **Create demo users:**
   ```bash
   python manage.py create_demo_users
   ```

### Step 4: Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to see your ChatMoji application!

## 👥 Demo Users

The demo users command creates the following test accounts:

| Email | Password | Name | Status |
|-------|----------|------|--------|
| john@example.com | password123 | John Doe | Online |
| jane@example.com | password123 | Jane Smith | Online |
| mike@example.com | password123 | Mike Johnson | Offline |
| sarah@example.com | password123 | Sarah Williams | Online |
| alex@example.com | password123 | Alex Brown | Offline |

## 🎯 Quick Start Guide

1. **Visit the landing page** at `http://127.0.0.1:8000`
2. **Register a new account** or login with demo credentials
3. **Add friends** by searching for users
4. **Start chatting** and watch every word become an emoji!

## 🔧 Key Features Explained

### Emoji Conversion
Every word you type gets automatically converted to an emoji. The system includes:
- 500+ mapped words to specific emojis
- Smart fallback emojis for unmapped words
- Real-time preview as you type

### Real-time Chat
- WebSocket-based messaging
- Typing indicators
- Online status indicators
- Read receipts
- Instant message delivery

### Friend System
- Send and receive friend requests
- Accept/reject requests
- View friends list
- See online/offline status

## 🚀 Next Steps (Future Enhancements)

After completing Phase 1, you can add:
- Group chat functionality
- File and image sharing
- Message search
- Push notifications
- Message reactions
- Voice messages
- Video calling

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🛡️ Security Features

- CSRF protection
- User authentication
- Input validation
- XSS prevention
- Secure file uploads

## 📞 Support

If you encounter any issues during setup:
1. Make sure Python 3.8+ is installed
2. Check that all files are in the correct directories
3. Verify virtual environment is activated
4. Run migrations if database errors occur

## 🎉 Congratulations!

You now have a fully functional chat application with emoji conversion! Start chatting and have fun watching every word transform into emojis!

---

**Happy Chatting! 💬✨**
# Dropix - Secure Cloud File Sharing Platform

Dropix is a premium, full-stack cloud file sharing web application. It features a modern user interface, robust authentication, seamless file management, and an administrative dashboard.

## Features

- **User Authentication:** Secure login, registration, and session management.
- **Modern Dashboard:** Upload, download, delete, and view your files in a premium interface with storage usage tracking.
- **Drag & Drop Upload:** Easy file uploading via drag and drop.
- **File Sharing:** Generate secure, unique public links to share files with anyone.
- **Admin Panel:** Separate dashboard for administrators to monitor users, files, and total storage across the platform.
- **Responsive Design:** Beautiful, fast, and mobile-friendly UI built with Tailwind CSS.
- **Dark Mode:** Built-in dark mode support.

## Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Werkzeug
- **Database:** SQLite (Easily swappable to PostgreSQL/MySQL via SQLAlchemy)
- **Frontend:** HTML5, CSS3, Tailwind CSS (via CDN), Alpine.js (via CDN), FontAwesome

## Prerequisites

- Python 3.8+ installed on your system.

## Installation & Setup Guide

1. **Clone or Download the Repository**
   Ensure you are in the project root directory (`dropix`).

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**
   ```bash
   pip install flask flask-sqlalchemy flask-login flask-bcrypt python-dotenv werkzeug
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```
   The database (`dropix.db`) and the `uploads` folder will be created automatically on the first run.
   
6. **Access the Application**
   Open your web browser and navigate to: `http://127.0.0.1:5000`

## Default Admin Credentials

An admin account is automatically created on initialization:
- **Email/Username:** 🔐
- **Password:** 🔐

*Ask The owner for email and password.*

## Project Structure

```
dropix/
│
├── app.py                 # Main application logic and routes
├── models.py              # Database models (User, File)
├── README.md              # Project documentation
│
├── uploads/               # Directory where user files are securely stored
│
└── templates/             # HTML Templates
    ├── base.html          # Base layout, Navbar, Footer
    ├── index.html         # Landing Page
    ├── login.html         # User & Admin Login
    ├── register.html      # Account Creation
    ├── dashboard.html     # User File Management Dashboard
    ├── admin.html         # Admin Monitoring Panel
    └── shared.html        # Public File Download Page
```

## Future Enhancements
To scale this project for production:
- Swap SQLite with PostgreSQL using `app.config['SQLALCHEMY_DATABASE_URI']`.
- Replace local `uploads` storage with AWS S3 using `boto3`.
- Integrate Stripe for premium storage tiers.
"# dropix" 

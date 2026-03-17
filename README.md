# Travel Blog System (Flask)

A simple travel blog system with:

- Public home page with latest posts and destinations
- Individual blog post pages
- Visitor comments on posts
- Search, destination filters, and sort by most discussed
- Save and unsave favorite stories
- Newsletter subscribe form
- About page and contact form
- Admin login and dashboard
- Create destination and create post forms
- Admin metrics and recent contact inbox preview
- SQLite database with auto-seeded sample data

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- SQLite

## Quick Start

1. Open terminal in this folder.
2. Create and activate a virtual environment.
3. Install dependencies.
4. Run the app.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

If pip is not available in your shell, use:

```powershell
python -m pip install -r requirements.txt
```

Open your browser at:

- http://127.0.0.1:5000/

## Admin Access

- URL: /admin/login
- Default username: admin
- Default password: admin123

Set your own credentials with environment variables:

```powershell
$env:ADMIN_USERNAME="your_admin"
$env:ADMIN_PASSWORD="your_secure_password"
$env:SECRET_KEY="replace-this-secret"
python app.py
```

## Notes

- Database file is created automatically as `travel_blog.db` in this folder.
- Seed data is inserted only once (first run).

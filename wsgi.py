# wsgi.py
# این فایل را در کنار app.py بسازید

from app import create_app

# ایجاد اپلیکیشن برای محیط production
app = create_app()

if __name__ == "__main__":
    app.run()
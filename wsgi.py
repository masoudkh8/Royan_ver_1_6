# wsgi.py
# این file را در کنار app.py بسofید

from app import create_app

# ایجاد application برای محیط production
app = create_app()

if __name__ == "__main__":
    app.run()
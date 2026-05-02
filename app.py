# app.py
import os

import click
from flask import  redirect, url_for
from itsdangerous import URLSafeTimedSerializer
import json
import config
from models import db,User,Order,DataProvider,Port,premium_request
from models.user import Role
from routes.admin.routes import admin_bp
from routes.users.routes import users_bp
from flask import Flask
from config import Config
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail ,Message
from routes.users import users_bp  # ✅ correct
from routes.admin import admin_bp
from routes.users import root_bp
from extensions import mail
from flask_babel import Babel, gettext, lazy_gettext as _
# from kavenegar import *

db = db
migrate = Migrate()
login_manager = LoginManager()
babel = Babel()

# List of supported languages (16 main world languages)
SUPPORTED_LANGUAGES = {
    'fa': 'Persian',
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano',
    'pt': 'Português',
    'ru': 'Русский',
    'zh': '中文',
    'ja': '日本語',
    'ko': '한국어',
    'ar': 'العربية',
    'tr': 'Türkçe',
    'hi': 'हिन्दी',
    'bn': 'বাংলা',
    'ur': 'Urdu'
}


# Function to read JSON dataset and store in database
def load_ports_from_dataset(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        for key in data:

            name = data[key].get('port_name')
            country = data[key].get("country")
            latitude = data[key].get('lat')
            longitude = data[key].get('long')
            # Check for required values
            if not name or not country or latitude is None or longitude is None:
                print(f"Invalid data: {data[key]}")
                continue
                # Check for duplicate Port
            new_port = Port(name=name,country=country, latitude=float(latitude), longitude=float(longitude))
            db.session.add(new_port)
            db.session.commit()
        print("Ports loaded successfully!")
    except FileNotFoundError:
        print("Dataset file not found!")
    except json.JSONDecodeError:
        print("Invalid JSON format in dataset file!")

def get_serializer():
    return URLSafeTimedSerializer(app.secret_key)

def create_app():

    # api = KavenegarAPI('5051786848506C45767269315634507077694A3157474E554B4E47775156385579774A38674E59587439633D')
    # params = {'sender': '2000660110', 'receptor': '09178001811', 'message': '.وب سرویس Message کوتاه کاوه نگار'}
    # response = api.sms_send(params)

    app = Flask(__name__)

    app.config.from_object(Config)

    # Database
    db.init_app(app)

    # Authentication

    migrate.init_app(app, db)
    login_manager.login_view = 'users.login'
    login_manager.login_message = "Please log in."
    login_manager.init_app(app)

    # Settings Email (example with Gmail)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'masoudkhalaj8@gmail.com'
    app.config['MAIL_PASSWORD'] = config.Config.MAIL_PASSWORD  # Do not use real password in production
    app.config['MAIL_DEFAULT_SENDER'] = 'masoudkhalaj8@gmail.com'

    # Settings Babel for internationalization
    app.config['BABEL_DEFAULT_LOCALE'] = 'fa'  # default language Persian
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    
    def get_locale():
        """Select language based on session or User header"""
        from flask import session, request
        # Priority is given to the language selected by the user
        if 'lang' in session:
            return session['lang']
        # If user does not select a language, use browser's Accept-Language
        return request.accept_languages.best_match(SUPPORTED_LANGUAGES.keys(), 'fa')
    
    babel.init_app(app, locale_selector=get_locale)


    mail.init_app(app)




    @app.context_processor
    def inject_roles():
        return {'Role': Role, 'SUPPORTED_LANGUAGES': SUPPORTED_LANGUAGES}

    @app.context_processor
    def inject_language_vars():
        """Inject language variables and prices to all templates"""
        from flask import session, request
        current_lang = session.get('lang', 'fa')
        return {
            'current_lang': current_lang,
            'supported_languages': SUPPORTED_LANGUAGES,
            '_': gettext,
            'PREMIUM_PRICE_USD': Config.PREMIUM_PRICE_USD,
            'SUBSCRIPTION_ANNUAL_IRR': Config.SUBSCRIPTION_ANNUAL_IRR,
            'SUBSCRIPTION_SEMI_ANNUAL_IRR': Config.SUBSCRIPTION_SEMI_ANNUAL_IRR
        }

    @app.route('/set_language/<lang_code>')
    def set_language(lang_code):
        """Change user language and save in session"""
        from flask import session, redirect, request
        if lang_code in SUPPORTED_LANGUAGES:
            session['lang'] = lang_code
        # Back to previous page or Home
        return redirect(request.referrer or url_for('root.index'))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.users import auth
    from routes.magazine import magazine_bp

    # Register blueprint
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(root_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(magazine_bp, url_prefix='/magazine')


    @app.cli.command("create-admin")
    @click.option('--username', prompt='Admin Username', help='Username for first Admin')
    @click.option('--email', prompt='Admin Email', help='Email for Admin')
    @click.option('--password', prompt='Admin Password', hide_input=True, confirmation_prompt=True,
                  help='Password for Admin')
    def create_admin(username, email, password):
        """Create first Admin user in the system"""
        with app.app_context():
            if User.query.filter_by(role=Role.ADMIN, is_active=True).first():
                click.echo(click.style("❌ An Admin already exists.", fg='red'))
                return

            username = username.strip()
            email = email.strip().lower()

            if len(username) < 3:
                click.echo(click.style("❌ Username must have at least 3 characters.", fg='red'))
                return
            if '@' not in email:
                click.echo(click.style("❌ Email address is invalid.", fg='red'))
                return
            if len(password) < 8:
                click.echo(click.style("❌ Password must have at least 8 characters.", fg='red'))
                return

            if User.query.filter_by(username=username, is_active=True).first():
                click.echo(click.style(f"❌ Username '{username}' is already taken.", fg='red'))
                return
            if User.query.filter_by(email=email, is_active=True).first():
                click.echo(click.style(f"❌ Email '{email}' is already in use.", fg='red'))
                return

            try:
                from werkzeug.security import generate_password_hash
                hashed = generate_password_hash(password)
                user = User(
                    username=username,
                    email=email,
                    password_hash=hashed,
                    role=Role.ADMIN,
                    is_premium=True,
                    is_active=True
                )
                db.session.add(user)
                db.session.commit()
                click.echo(click.style(f"✅ Admin '{username}' created successfully.", fg='green'))
            except Exception as e:
                db.session.rollback()
                click.echo(click.style(f"❌ Database error: {e}", fg='red'))


    # Create database
    with app.app_context():

        # Dataset file path
        # dataset_file = 'static/files/ports.json'  # JSON file containing port information
        # load_ports_from_dataset(dataset_file)

        db.create_all()
        print("✅ Database and tables created.")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
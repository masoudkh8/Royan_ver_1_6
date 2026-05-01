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
from routes.users import users_bp  # ✅ درست
from routes.admin import admin_bp
from routes.users import root_bp
from extensions import mail
# from kavenegar import *

db = db
migrate = Migrate()
login_manager = LoginManager()


# تابع برای خواندن دیتاست JSON و ذخیره در پایگاه داده
def load_ports_from_dataset(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        for key in data:

            name = data[key].get('port_name')
            country = data[key].get("country")
            latitude = data[key].get('lat')
            longitude = data[key].get('long')
            # بررسی وجود مقادیر ضروری
            if not name or not country or latitude is None or longitude is None:
                print(f"Invalid data: {data[key]}")
                continue
                # بررسی تکراری نبودن بندر
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
    # params = {'sender': '2000660110', 'receptor': '09178001811', 'message': '.وب سرویس پیام کوتاه کاوه نگار'}
    # response = api.sms_send(params)

    app = Flask(__name__)

    app.config.from_object(Config)

    # دیتابیس
    db.init_app(app)

    # احراز هویت

    migrate.init_app(app, db)
    login_manager.login_view = 'users.login'
    login_manager.login_message = "لطفاً وارد شوید."
    login_manager.init_app(app)

    # تنظیمات ایمیل (مثال با Gmail)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'masoudkhalaj8@gmail.com'
    app.config['MAIL_PASSWORD'] = config.Config.MAIL_PASSWORD  # از رمز واقعی استفاده نکنید
    app.config['MAIL_DEFAULT_SENDER'] = 'masoudkhalaj8@gmail.com'





    mail.init_app(app)




    @app.context_processor
    def inject_roles():
        return {'Role': Role}

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.users import auth
    from routes.magazine import magazine_bp

    # ثبت بلوپرینت
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(root_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(magazine_bp, url_prefix='/magazine')


    @app.cli.command("create-admin")
    @click.option('--username', prompt='نام کاربری ادمین', help='نام کاربری برای ادمین اول')
    @click.option('--email', prompt='ایمیل ادمین', help='ایمیل ادمین')
    @click.option('--password', prompt='رمز عبور ادمین', hide_input=True, confirmation_prompt=True,
                  help='رمز عبور ادمین')
    def create_admin(username, email, password):
        """ایجاد اولین کاربر ادمین در سیستم"""
        with app.app_context():
            if User.query.filter_by(role=Role.ADMIN, is_active=True).first():
                click.echo(click.style("❌ قبلاً یک ادمین وجود دارد.", fg='red'))
                return

            username = username.strip()
            email = email.strip().lower()

            if len(username) < 3:
                click.echo(click.style("❌ نام کاربری باید حداقل 3 کاراکتر داشته باشد.", fg='red'))
                return
            if '@' not in email:
                click.echo(click.style("❌ آدرس ایمیل نامعتبر است.", fg='red'))
                return
            if len(password) < 8:
                click.echo(click.style("❌ رمز عبور باید حداقل 8 کاراکتر داشته باشد.", fg='red'))
                return

            if User.query.filter_by(username=username, is_active=True).first():
                click.echo(click.style(f"❌ نام کاربری '{username}' قبلاً گرفته شده است.", fg='red'))
                return
            if User.query.filter_by(email=email, is_active=True).first():
                click.echo(click.style(f"❌ ایمیل '{email}' قبلاً استفاده شده است.", fg='red'))
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
                click.echo(click.style(f"✅ ادمین '{username}' با موفقیت ایجاد شد.", fg='green'))
            except Exception as e:
                db.session.rollback()
                click.echo(click.style(f"❌ خطای پایگاه داده: {e}", fg='red'))


    # ایجاد دیتابیس
    with app.app_context():

        # مسیر فایل دیتاست
        # dataset_file = 'static/files/ports.json'  # فایل JSON حاوی اطلاعات پورت‌ها
        # load_ports_from_dataset(dataset_file)

        db.create_all()
        print("✅ دیتابیس و جداول ایجاد شدند.")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
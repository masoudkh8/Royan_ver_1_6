# config.py
import os
from dotenv import load_dotenv

SUPPORTED_LANGUAGES = {
    'fa': 'فارسی',
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
    'ur': 'اردو'
}

RTL_LANGUAGES = ['fa', 'ar', 'ur']


load_dotenv()


class Config:
    DEBUG = False
    D_STATE = "0"  #0 = False , 1 = True
    AMOOTSMS_TOKEN = "052877AF60F77DE6FA1E58D0761A339C5D8C6BAA"
    KAVENEGAR_API_KEY = "5051786848506C45767269315634507077694A3157474E554B4E47775156385579774A38674E59587439633D"
    SECRET_KEY = os.environ.get("SECRET_KEY")

    #SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_PASSWORD= 'jcdhiqoktqtindfg'
    
    # تنظیمات قیمت‌ها
    PREMIUM_PRICE_USD = 10000  # قیمت ارتقاء به کاربر ویژه به دلار
    SUBSCRIPTION_ANNUAL_IRR = 1200000  # اشتراک سالیانه مجله به تومان
    SUBSCRIPTION_SEMI_ANNUAL_IRR = 650000  # اشتراک شش ماهه مجله به تومان
    
    # تنظیمات آپلود فایل مجله
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAGAZINE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'magazines')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # حداکثر حجم فایل 50 مگابایت
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}


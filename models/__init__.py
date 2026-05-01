# models/__init__.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ایمپورت مدل‌ها
from .user import User
from .order import Order
from .notification import Notification
from .message import Message
from .provider import DataProvider
from .port import Port
from .premium_request import PremiumRequest
from .magazine import Magazine, MagazineIssue, SponsorshipRequest, AdvertisementRequest, Subscription
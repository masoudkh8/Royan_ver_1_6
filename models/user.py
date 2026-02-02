# models/user.py
# from flask_sqlalchemy import SQLAlchemy
from . import db
from flask_login import UserMixin
from enum import Enum

# db = SQLAlchemy()

class Role(Enum):
    BUYER = 'buyer'
    SELLER = 'seller'
    BROKER = 'broker'
    ADMIN = 'admin'

    @staticmethod
    def has_value(value):
        return value in [role.value for role in Role]


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)
    # role = db.Column(db.Enum(Role), default=Role.BUYER, nullable=False)
    notifications = db.relationship('Notification', back_populates='user', lazy='dynamic',cascade='all, delete-orphan')
    # notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan',
    #                                 foreign_keys='Notification.user_id')
    company_name = db.Column(db.String(100))
    country = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)  # ✅ فعال/غیرفعال
    is_premium = db.Column(db.Boolean, default=False)
    premium_since = db.Column(db.DateTime, default=None)
    premium_requests = db.relationship('PremiumRequest', back_populates='user', cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=db.func.now())

    # def __repr__(self):
    #     return f"<User {self.username} | {self.role.value} | Premium: {self.is_premium}>"
    @property
    def unread_notifications_count(self):
        return self.notifications.filter_by(user_id=self.id, is_read=False).count()

    def __repr__(self):
        return f"<User {self.username}>"
# # models/order.py
# from . import db
# from datetime import datetime
# import pytz
# tehran_tz = pytz.timezone('Asia/Tehran')
# from enum import Enum
# from sqlalchemy import Enum as SqlEnum
# # from flask_sqlalchemy import SQLAlchemy
#
#
# # db = SQLAlchemy()
#
# class OrderStatus(Enum):
#     PENDING = "pending"           # در انتظار تأیید
#     CONFIRMED = "confirmed"       # تأیید شده
#     IN_TRANSIT = "in_transit"     # در حال حمل
#     DELIVERED = "delivered"       # تحویل داده شده
#     CANCELLED = "cancelled"       # Cancel شده
#
# class Order(db.Model):
#     __tablename__ = 'orders'
#
#     id = db.Column(db.Integer, primary_key=True)
#     product = db.Column(db.String(100), nullable=False)  # مثلاً Wheat, Rice
#     quantity_tons = db.Column(db.Float, nullable=False)  # کمیت to Ton
#     price_per_ton = db.Column(db.Float, nullable=False)  # قیمت هر Ton (دلار)
#     total_price = db.Column(db.Float, nullable=False)    # محاسto: quantity * price
#
#     # پورت مبدأ و Destination
#     origin_port = db.Column(db.String(100), nullable=False)
#     destination_port = db.Column(db.String(100), nullable=False)
#
#     # Description
#     notes = db.Column(db.Text, nullable=True)
#
#     # Order status
#     status = db.Column(SqlEnum(OrderStatus), default=OrderStatus.PENDING)
#
#     # روابط با Users
#     buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     broker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
#
#     # Date‌ها
#     created_at = db.Column(db.DateTime, default=datetime.now(tehran_tz))
#     updated_at = db.Column(db.DateTime, default=datetime.now(tehran_tz), onupdate=datetime.now(tehran_tz))
#     shipped_at = db.Column(db.DateTime,default=datetime.now(tehran_tz) ,nullable=True)
#     delivered_at = db.Column(db.DateTime,default=datetime.now(tehran_tz) ,nullable=True)
#
#     # رابطه معکوس (برای دسترسی آسان)
#     buyer = db.relationship('User', foreign_keys=[buyer_id], backref='purchases')
#     seller = db.relationship('User', foreign_keys=[seller_id], backref='sales')
#     broker = db.relationship('User', foreign_keys=[broker_id], backref='brokered_orders')
#
#     # def __repr__(self):
#     #     return f"<Order {self.id} | {self.product} | {self.quantity_tons}T | {self.status.value}>"
#
#     def calculate_total(self):
#         """محاسto قیمت کل"""
#         self.total_price = self.quantity_tons * self.price_per_ton
#
#     # def mark_as_shipped(self):
#     #     """علامت‌گذاری to عنوان Send شده"""
#     #     self.status = OrderStatus.IN_TRANSIT
#     #     self.shipped_at = datetime.utcnow()
#     #
#     # def mark_as_delivered(self):
#     #     """علامت‌گذاری to عنوان تحویل داده شده"""
#     #     self.status = OrderStatus.DELIVERED
#     #     self.delivered_at = datetime.utcnow()






# models/order.py
from . import db
from datetime import datetime
import pytz
from enum import Enum
from sqlalchemy import Enum as SqlEnum

# Tonظیم منطقه زمانی تهران
tehran_tz = pytz.timezone('Asia/Tehran')

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(100), nullable=False)
    quantity_tons = db.Column(db.Float, nullable=False)
    price_per_ton = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)  # محاسto شده

    origin_port = db.Column(db.String(100), nullable=False)
    destination_port = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    status = db.Column(SqlEnum(OrderStatus), default=OrderStatus.PENDING)

    # 🔑 کلیدهای Outsideی — نام جدول درست: 'users'
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    broker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # Date‌ها — استفاده از lambda برای ارزیابی در زمان اجرا
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz), onupdate=lambda: datetime.now(tehran_tz))
    shipped_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)

    # رابطه‌ها
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='buyer_orders')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='seller_orders')
    broker = db.relationship('User', foreign_keys=[broker_id], backref='brokered_orders')

    def calculate_total(self):
        """محاسto قیمت کل: quantity * price"""
        self.total_price = self.quantity_tons * self.price_per_ton

    def __repr__(self):
        return f"<Order {self.id} | {self.product} | {self.quantity_tons}T | {self.status.value}>"
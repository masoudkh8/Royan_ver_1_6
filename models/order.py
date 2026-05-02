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
#     PENDING = "pending"           # Pending approval
#     CONFIRMED = "confirmed"       # Confirmed
#     IN_TRANSIT = "in_transit"     # In transit
#     DELIVERED = "delivered"       # Delivered
#     CANCELLED = "cancelled"       # Cancelled
#
# class Order(db.Model):
#     __tablename__ = 'orders'
#
#     id = db.Column(db.Integer, primary_key=True)
#     product = db.Column(db.String(100), nullable=False)  # مثلاً Wheat, Rice
#     quantity_tons = db.Column(db.Float, nullable=False)  # Quantity in tons
#     price_per_ton = db.Column(db.Float, nullable=False)  # Price per ton (USD)
#     total_price = db.Column(db.Float, nullable=False)    # محاسto: quantity * price
#
#     # پورت مبدأ و Destination
#     origin_port = db.Column(db.String(100), nullable=False)
#     destination_port = db.Column(db.String(100), nullable=False)
#
#     # Notes
#     notes = db.Column(db.Text, nullable=True)
#
#     # Order status
#     status = db.Column(SqlEnum(OrderStatus), default=OrderStatus.PENDING)
#
#     # User relationships
#     buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     broker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
#
#     # Dates
#     created_at = db.Column(db.DateTime, default=datetime.now(tehran_tz))
#     updated_at = db.Column(db.DateTime, default=datetime.now(tehran_tz), onupdate=datetime.now(tehran_tz))
#     shipped_at = db.Column(db.DateTime,default=datetime.now(tehran_tz) ,nullable=True)
#     delivered_at = db.Column(db.DateTime,default=datetime.now(tehran_tz) ,nullable=True)
#
#     # Inverse relationship (For easy access)
#     buyer = db.relationship('User', foreign_keys=[buyer_id], backref='purchases')
#     seller = db.relationship('User', foreign_keys=[seller_id], backref='sales')
#     broker = db.relationship('User', foreign_keys=[broker_id], backref='brokered_orders')
#
#     # def __repr__(self):
#     #     return f"<Order {self.id} | {self.product} | {self.quantity_tons}T | {self.status.value}>"
#
#     def calculate_total(self):
#         """Calculate total price"""
#         self.total_price = self.quantity_tons * self.price_per_ton
#
#     # def mark_as_shipped(self):
#     #     """Mark as sent"""
#     #     self.status = OrderStatus.IN_TRANSIT
#     #     self.shipped_at = datetime.utcnow()
#     #
#     # def mark_as_delivered(self):
#     #     """Mark as delivered"""
#     #     self.status = OrderStatus.DELIVERED
#     #     self.delivered_at = datetime.utcnow()






# models/order.py
from . import db
from datetime import datetime
import pytz
from enum import Enum
from sqlalchemy import Enum as SqlEnum

# Tonظیم منطقه timeی تهران
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

    # 🔑 keyهای Outsideی — Correct table name: 'users'
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    broker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # Dates — استفاده of lambda برای ارزیابی در time اجرا
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz), onupdate=lambda: datetime.now(tehran_tz))
    shipped_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='buyer_orders')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='seller_orders')
    broker = db.relationship('User', foreign_keys=[broker_id], backref='brokered_orders')

    def calculate_total(self):
        """Calculate total price: quantity * price"""
        self.total_price = self.quantity_tons * self.price_per_ton

    def __repr__(self):
        return f"<Order {self.id} | {self.product} | {self.quantity_tons}T | {self.status.value}>"
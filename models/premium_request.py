# models/premium_request.py
from . import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from datetime import datetime
import pytz
tehran_tz = pytz.timezone('Asia/Tehran')

class PremiumRequest(db.Model):
    __tablename__ = 'premium_requests'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    requested_phone = db.Column(db.String(15), nullable=False)
    # Status Steps
    phone_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    docs_verified = Column(Boolean, default=False)
    payment_verified = Column(Boolean, default=False)

    # Verification code
    phone_verification_code = Column(String(6))
    email_verification_token = Column(String(120))

    # Upload documents
    passport_file = Column(String(200))
    license_file = Column(String(200))
    payment_receipt = Column(String(200))

    # Status کلی
    status = Column(String(20), default='pending')  # pending, approved, rejected
    submitted_at = Column(DateTime, default=datetime.now(tehran_tz))
    reviewed_at = Column(DateTime ,default=datetime.now(tehran_tz))
    notes = Column(Text)

    # Relationship
    # user = db.relationship('User', backref='premium_requests')
    user = db.relationship('User', back_populates='premium_requests')
# models/magazine.py

from . import db
from datetime import datetime

class Magazine(db.Model):
    """مدل Info کلی magazine"""
    __tablename__ = 'magazines'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default='Tasvir Magazine')
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship with magazine issues
    issues = db.relationship('MagazineIssue', backref='magazine', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Magazine {self.title}>'


class MagazineIssue(db.Model):
    """Magazine issues model"""
    __tablename__ = 'magazine_issues'
    
    id = db.Column(db.Integer, primary_key=True)
    magazine_id = db.Column(db.Integer, db.ForeignKey('magazines.id'), nullable=False)
    issue_number = db.Column(db.Integer, nullable=False)  # Issue number
    title = db.Column(db.String(200), nullable=False)  # Issue title
    description = db.Column(db.Text)  # Notes شماره
    cover_image_url = db.Column(db.String(500))  # Cover image URL
    file_url = db.Column(db.String(500), nullable=False)  # URL file PDF برای download
    file_size = db.Column(db.String(50))  # File size
    publish_date = db.Column(db.Date, nullable=False)  # Date publish
    is_published = db.Column(db.Boolean, default=False)  # Status publish
    download_count = db.Column(db.Integer, default=0)  # Download count
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<MagazineIssue {self.issue_number} - {self.title}>'


class SponsorshipRequest(db.Model):
    """مدل Request Sponsorship"""
    __tablename__ = 'sponsorship_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # اگر User logین کRejectه باشد
    full_name = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(200))  # Company name
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text)  # Message و Notes
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with user
    user = db.relationship('User', backref=db.backref('sponsorship_requests', lazy=True))
    
    def __repr__(self):
        return f'<SponsorshipRequest {self.email}>'


class AdvertisementRequest(db.Model):
    """مدل Request Advertisement در magazine"""
    __tablename__ = 'advertisement_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    full_name = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(200))
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    ad_type = db.Column(db.String(50))  # Ad type: full_page, half_page, quarter_page, etc.
    message = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with user
    user = db.relationship('User', backref=db.backref('advertisement_requests', lazy=True))
    
    def __repr__(self):
        return f'<AdvertisementRequest {self.email}>'


class Subscription(db.Model):
    """مدل Annual Subscription magazine"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)  # address postی برای Send نسخه چappی
    subscription_type = db.Column(db.String(50), default='annual')  # annual, semi_annual
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=False)
    payment_status = db.Column(db.String(50), default='pending')  # pending, paid, failed
    price = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with user
    user = db.relationship('User', backref=db.backref('subscriptions', lazy=True))
    
    def __repr__(self):
        return f'<Subscription {self.email}>'

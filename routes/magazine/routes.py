# routes/magazine/routes.py
from flask import render_template, request, redirect, url_for, flash, send_from_directory, current_app
from . import magazine_bp
from models import db, MagazineIssue, SponsorshipRequest, AdvertisementRequest, Subscription
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# routeهای general برای Show magazine
@magazine_bp.route('/')
def index():
    """Home magazine - Show شماره‌های in stock"""
    issues = MagazineIssue.query.filter_by(is_published=True).order_by(MagazineIssue.issue_number.desc()).all()
    return render_template('magazine/index.html', issues=issues)

@magazine_bp.route('/download/<int:issue_id>')
def download_issue(issue_id):
    """download file دیجیتال magazine"""
    issue = MagazineIssue.query.get_or_404(issue_id)
    
    if not issue.is_published:
        flash('This issue is not yet published.', 'error')
        return redirect(url_for('magazine.index'))
    
    # route file را برگRejectانید
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'magazines', issue.file_path)
    
    if os.path.exists(file_path):
        return send_from_directory(
            os.path.join(current_app.config['UPLOAD_FOLDER'], 'magazines'),
            issue.file_path,
            as_attachment=True,
            download_name=f"imazheh-issue-{issue.issue_number}.pdf"
        )
    else:
        flash('Magazine file not found.', 'error')
        return redirect(url_for('magazine.index'))

# Form Request Sponsorship
@magazine_bp.route('/sponsorship', methods=['GET', 'POST'])
def sponsorship_request():
    """ثبت Request Sponsorship"""
    if request.method == 'POST':
        name = request.form.get('name')
        company = request.form.get('company')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        if not all([name, email, phone]):
            flash('Please fill in the required fields.', 'error')
            return redirect(url_for('magazine.sponsorship_request'))
        
        new_request = SponsorshipRequest(
            name=name,
            company=company,
            email=email,
            phone=phone,
            message=message
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        flash('Your sponsorship request has been successfully submitted. We will contact you soon.', 'success')
        return redirect(url_for('magazine.index'))
    
    return render_template('magazine/sponsorship.html')

# Form Request Advertisement
@magazine_bp.route('/advertisement', methods=['GET', 'POST'])
def advertisement_request():
    """ثبت Request Advertisement در magazine"""
    if request.method == 'POST':
        name = request.form.get('name')
        company = request.form.get('company')
        email = request.form.get('email')
        phone = request.form.get('phone')
        ad_type = request.form.get('ad_type')
        size = request.form.get('size')
        duration = request.form.get('duration')
        message = request.form.get('message')
        
        if not all([name, email, phone, ad_type]):
            flash('Please fill in the required fields.', 'error')
            return redirect(url_for('magazine.advertisement_request'))
        
        new_request = AdvertisementRequest(
            name=name,
            company=company,
            email=email,
            phone=phone,
            ad_type=ad_type,
            size=size,
            duration=duration,
            message=message
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        flash('Your advertising request has been successfully submitted. We will contact you soon.', 'success')
        return redirect(url_for('magazine.index'))
    
    return render_template('magazine/advertisement.html')

# Form Annual Subscription
@magazine_bp.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    """Register Annual Subscription"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        subscription_type = request.form.get('subscription_type')
        
        if not all([name, email, phone, address]):
            flash('Please fill in the required fields.', 'error')
            return redirect(url_for('magazine.subscribe'))
        
        new_subscription = Subscription(
            name=name,
            email=email,
            phone=phone,
            address=address,
            subscription_type=subscription_type,
            start_date=datetime.utcnow(),
            is_active=True
        )
        
        db.session.add(new_subscription)
        db.session.commit()
        
        flash('Your annual subscription has been successfully registered. Information will be sent soon.', 'success')
        return redirect(url_for('magazine.index'))
    
    return render_template('magazine/subscribe.html')

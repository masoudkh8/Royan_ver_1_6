# routes/admin/requests.py
from flask import flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from models import db
from models.premium_request import PremiumRequest
from . import admin_bp


def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("❌ Access denied.")
            return redirect(url_for('users.profile'))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route('/premium_requests')
@admin_required
def premium_requests():
    requests = PremiumRequest.query.order_by(PremiumRequest.submitted_at.desc()).all()
    return render_template('admin/premium_requests.html', requests=requests)


@admin_bp.route('/approve_premium/<int:req_id>', methods=['POST'])
@admin_required
def approve_premium(req_id):
    req = PremiumRequest.query.get_or_404(req_id)
    req.status = 'approved'
    req.reviewed_at = db.func.now()
    req.user.is_premium = True
    db.session.commit()

    # Notification to User
    send_notification(req.user, "✅ Upgrade request شما تأیید شد.")
    flash(f"✅ User {req.user.username} upgraded to premium.")
    return redirect(url_for('admin.premium_requests'))


@admin_bp.route('/reject_premium/<int:req_id>', methods=['POST'])
@admin_required
def reject_premium(req_id):
    req = PremiumRequest.query.get_or_404(req_id)
    req.status = 'rejected'
    req.reviewed_at = db.func.now()
    db.session.commit()

    # Notification to User
    send_notification(req.user, "❌ Your upgrade request has been rejected. می‌توانید again تلاش کنید.")
    flash(f"❌ request from User {req.user.username} rejected.")
    return redirect(url_for('admin.premium_requests'))


# تابع Notification Insideی (مثال ساده)
def send_notification(user, message):
    # در عمل: ذNoه در جدول Notifications
    print(f"📩 نوتیفیکیشن to {user.username}: {message}")
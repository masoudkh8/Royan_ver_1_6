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
            flash("❌ دسترسی ممنوع.")
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

    # اعلان به کاربر
    send_notification(req.user, "✅ درخواست ارتقاء شما تأیید شد.")
    flash(f"✅ کاربر {req.user.username} به ویژه ارتقاء یافت.")
    return redirect(url_for('admin.premium_requests'))


@admin_bp.route('/reject_premium/<int:req_id>', methods=['POST'])
@admin_required
def reject_premium(req_id):
    req = PremiumRequest.query.get_or_404(req_id)
    req.status = 'rejected'
    req.reviewed_at = db.func.now()
    db.session.commit()

    # اعلان به کاربر
    send_notification(req.user, "❌ درخواست ارتقاء شما رد شد. می‌توانید دوباره تلاش کنید.")
    flash(f"❌ درخواست کاربر {req.user.username} رد شد.")
    return redirect(url_for('admin.premium_requests'))


# تابع اعلان داخلی (مثال ساده)
def send_notification(user, message):
    # در عمل: ذخیره در جدول Notifications
    print(f"📩 نوتیفیکیشن به {user.username}: {message}")
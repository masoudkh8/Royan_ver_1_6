# routes/admin/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from models import db, Notification
from models.user import User, Role
from models.premium_request import PremiumRequest

from datetime import datetime
import pytz
tehran_tz = pytz.timezone('Asia/Tehran')

from functools import wraps
from flask import request, flash, redirect, url_for, render_template
from flask_login import login_user
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import admin_bp



# ---------------------------------------
# Decorator: فقط Admin دسترسی داشته ok
# ---------------------------------------

@admin_bp.route('')
@admin_bp.route('/admin')
def admin_index():
    return redirect(url_for('admin.login'))

def admin_required(f):
    @wraps(f)  # ✅ این خط issue رو حل می‌کنه
    def decorated_function(*args, **kwargs):
        # ✅ first چک کن User واrejectedه باشد
        if not current_user.is_authenticated:
            flash("❌ Please log in first.")
            return redirect(url_for('users.login'))
        print(current_user.role)
        if  current_user.role != Role.ADMIN:
            flash("❌ Access denied: Only admins can access this page.", "error")
            return redirect(url_for('users.profile'))
        return f(*args, **kwargs)

    return decorated_function


# ---------------------------------------
# Dashboard Admin
# ---------------------------------------
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    premium_requests = PremiumRequest.query.count()
    pending_requests = PremiumRequest.query.filter_by(status='pending').count()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           premium_requests=premium_requests,
                           pending_requests=pending_requests)


# ---------------------------------------
# User Management
# ---------------------------------------
# @admin_bp.route('/users')
# @admin_required
# def manage_users():
#     page = request.args.get('page', 1, type=int)
#     per_page = 10
#     # users = User.query.order_by(User.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
#     users = User.query.filter_by(is_active=True).order_by(User.id.desc()).paginate(
#         page=page,
#         per_page=per_page,
#         error_out=False
#     )
#     return render_template('admin/manage_users.html', users=users)
@admin_bp.route('/users')
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    status_filter = request.args.get('status', 'active')

    query = User.query

    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)

    users = query.order_by(User.id.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # ✅ محاسto quantity در بک‌اند
    total_active = User.query.filter_by(is_active=True).count()
    total_inactive = User.query.filter_by(is_active=False).count()

    return render_template(
        'admin/manage_users.html',
        users=users,
        status_filter=status_filter,
        total_active=total_active,
        total_inactive=total_inactive
    )
# ---------------------------------------
# change User role
# ---------------------------------------
@admin_bp.route('/user/<int:user_id>/role', methods=['POST'])
@admin_required
def change_user_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')

    if not Role.has_value(new_role):
        flash("❌ Invalid role.", "error")
    else:
        user.role = Role(new_role)
        # print(new_role)
        if new_role=="admin":
            user.is_premium=True
        db.session.commit()
        flash(f"✅ User role {user.username} to '{new_role}' changed.", "success")
    return redirect(url_for('admin.manage_users'))


# ---------------------------------------
# Upgrade Requests to Premium User
# ---------------------------------------
@admin_bp.route('/premium_requests')
@admin_required
def premium_requests():
    status_filter = request.args.get('status', 'all')
    query = PremiumRequest.query.order_by(PremiumRequest.submitted_at.desc())

    if status_filter == 'pending':
        query = query.filter_by(status='pending')
    elif status_filter == 'approved':
        query = query.filter_by(status='approved')
    elif status_filter == 'rejected':
        query = query.filter_by(status='rejected')

    requests = query.all()
    return render_template('admin/premium_requests.html', requests=requests, status_filter=status_filter)


# ---------------------------------------
# تأیید Upgrade request
# ---------------------------------------
@admin_bp.route('/approve_premium/<int:req_id>', methods=['POST'])
@admin_required
def approve_premium(req_id):
    req = PremiumRequest.query.get_or_404(req_id)
    req.status = 'approved'
    req.reviewed_at = datetime.now(tehran_tz)
    req.user.is_premium = True
    db.session.commit()

    flash(f"✅ User '{req.user.username}' successfully upgraded to Premium User.", "success")
    return redirect(url_for('admin.premium_requests'))


# ---------------------------------------
# Reject Upgrade request
# ---------------------------------------
@admin_bp.route('/reject_premium/<int:req_id>', methods=['POST'])
@admin_required
def reject_premium(req_id):
    req = PremiumRequest.query.get_or_404(req_id)
    req.status = 'rejected'
    req.reviewed_at = datetime.now(tehran_tz)
    db.session.commit()

    flash(f"❌ Upgrade request User '{req.user.username}' rejected.", "warning")
    return redirect(url_for('admin.premium_requests'))


# ---------------------------------------
# view Details request
# ---------------------------------------
@admin_bp.route('/premium_request/<int:req_id>')
@admin_required
def view_premium_request(req_id):
    req = PremiumRequest.query.get_or_404(req_id)
    return render_template('admin/view_premium_request.html', req=req)


# ---------------------------------------
# Delete User (با احتیاط)
# ---------------------------------------
@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    Notification.query.filter_by(user_id=user_id).delete()
    if current_user.id == user_id:
        flash("❌ You cannot delete yourself.", "error")
        return redirect(url_for('admin.manage_users'))

    user = User.query.get_or_404(user_id)
    username = user.username

    # Delete Upgrade request اگر وجود داشت
    req = PremiumRequest.query.filter_by(user_id=user.id).first()
    if req:
        db.session.delete(req)

    user.is_active = False
    # db.session.delete(user)
    db.session.commit()
    print(current_user.id , current_user.username)
    flash(f"✅ User '{username}' successfully deleted.", "success")
    return redirect(url_for('admin.manage_users'))

####################3
#
# @admin_bp.route('/deactivate_user/<int:user_id>', methods=['POST'])
# @admin_required
# def deactivate_user(user_id):
#     user = User.query.get_or_404(user_id)
#
#     if user.role == Role.ADMIN:
#         flash("❌ You cannot deactivate an Admin.")
#         return redirect(url_for('admin.users_list'))
#
#     user.is_active = False
#     db.session.commit()
#
#     flash(f"✅ User {user.username} successfully deactivated.")
#     return redirect(url_for('admin.users_list'))
#
# @admin_bp.route('/activate_user/<int:user_id>', methods=['POST'])
# @admin_required
# def activate_user(user_id):
#     user = User.query.get_or_404(user_id)
#     user.is_active = True
#     db.session.commit()
#     flash(f"✅ User {user.username} again activated.")
#     return redirect(url_for('admin.users_list'))

# ---------------------------------------
# Inactive‌سofی User
# ---------------------------------------
@admin_bp.route('/user/<int:user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(user_id):
    if current_user.id == user_id:
        flash("❌ You cannot deactivate yourself.")
        return redirect(url_for('admin.manage_users'))

    user = User.query.get_or_404(user_id)
    if user.role == Role.ADMIN:
        flash("❌ You cannot deactivate another Admin.")
        return redirect(url_for('admin.manage_users'))

    user.is_active = False
    db.session.commit()
    flash(f"✅ User '{user.username}' deactivated.")
    return redirect(url_for('admin.manage_users', status=request.args.get('status', 'active')))


# ---------------------------------------
# Active‌سofی User
# ---------------------------------------
@admin_bp.route('/user/<int:user_id>/activate', methods=['POST'])
@admin_required
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash(f"✅ User '{user.username}' activated.")
    return redirect(url_for('admin.manage_users', status=request.args.get('status', 'active')))



# Login page
@admin_bp.route('/login')
def login():
    return render_template('admin/login.html', current_year=datetime.now().year)

# پRejectofش Login
@admin_bp.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email, is_active=True).first()

    if user and check_password_hash(user.password_hash, password):
        if user.role ==  Role.ADMIN:
            login_user(user)
            flash("✅ Welcome, Admin!", "success")
            return redirect(url_for('admin.dashboard'))
        else:
            print(user.role)
            print(user)
            flash("❌ Access denied: Only admins can log in.", "error")
    else:
        flash("❌ Email or Password is incorrect.", "error")

    return redirect(url_for('admin.login'))
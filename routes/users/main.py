# import os
# from flask import request, flash, redirect, url_for, render_template
# from flask import current_app  # برای دسترسی to متغیرهای محیطی
# from models import db
# from models.user import User, Role
# from werkzeug.security import generate_password_hash
# from . import users_bp
#
# @users_bp.route('/create_first_admin', methods=['GET', 'POST'])
# def create_first_admin():
#     # ✅ 1. بررسی: آیا Admin وجود داReject؟
#     if User.query.filter_by(role=Role.ADMIN, is_active=True).first():
#         flash("❌ An Admin already exists.", "error")
#         return redirect(url_for('users.login'))
#
#     # ✅ 2. (اختیاری) Active‌سازی با متغیر محیطی — برای امنیت More
#     if not current_app.config.get('ALLOW_CREATE_FIRST_ADMIN'):
#         flash("❌ ایجاد Admin Inactive است.", "error")
#         return redirect(url_for('users.login'))
#
#     if request.method == 'POST':
#         try:
#             username = request.form.get('username', '').strip()
#             email = request.form.get('email', '').strip()
#             password = request.form.get('password', '')
#
#             # ✅ اعتبارسنجی Loginی
#             if not username or not email or not password:
#                 flash("❌ تمام فیلدها الزامی هسTonد.", "error")
#                 return render_template('admin/create_first_admin.html')
#
#             if len(username) < 3:
#                 flash("❌ Username must be at least 3 characters.", "error")
#                 return render_template('admin/create_first_admin.html')
#
#             if len(password) < 8:
#                 flash("❌ Password must be at least 8 characters.", "error")
#                 return render_template('admin/create_first_admin.html')
#
#             # ✅ بررسی تکراری بودن
#             if User.query.filter_by(username=username, is_active=True).first():
#                 flash("❌ Username already taken.", "error")
#                 return render_template('admin/create_first_admin.html')
#
#             if User.query.filter_by(email=email, is_active=True).first():
#                 flash("❌ Email already in use.", "error")
#                 return render_template('admin/create_first_admin.html')
#
#             # ✅ ایجاد Admin
#             hashed = generate_password_hash(password)
#             user = User(
#                 username=username,
#                 email=email,
#                 password_hash=hashed,
#                 role=Role.ADMIN,
#                 is_premium=True,
#                 is_active=True
#             )
#
#             db.session.add(user)
#             db.session.commit()
#
#             flash("✅ Admin اول successfully ایجاد شد.", "success")
#             return redirect(url_for('admin.login'))
#
#         except Exception as e:
#             db.session.rollback()
#             flash("❌ Errorیی رخ داد. لطفاً again تلاش کنید.", "error")
#             current_app.logger.error(f"Error creating first admin: {e}")
#             return render_template('admin/create_first_admin.html')
#
#     # GET: Show فرم
#     return render_template('admin/create_first_admin.html')
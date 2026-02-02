# import os
# from flask import request, flash, redirect, url_for, render_template
# from flask import current_app  # برای دسترسی به متغیرهای محیطی
# from models import db
# from models.user import User, Role
# from werkzeug.security import generate_password_hash
# from . import users_bp
#
# @users_bp.route('/create_first_admin', methods=['GET', 'POST'])
# def create_first_admin():
#     # ✅ 1. بررسی: آیا ادمین وجود دارد؟
#     if User.query.filter_by(role=Role.ADMIN, is_active=True).first():
#         flash("❌ قبلاً یک ادمین وجود دارد.", "error")
#         return redirect(url_for('users.login'))
#
#     # ✅ 2. (اختیاری) فعال‌سازی با متغیر محیطی — برای امنیت بیشتر
#     if not current_app.config.get('ALLOW_CREATE_FIRST_ADMIN'):
#         flash("❌ ایجاد ادمین غیرفعال است.", "error")
#         return redirect(url_for('users.login'))
#
#     if request.method == 'POST':
#         try:
#             username = request.form.get('username', '').strip()
#             email = request.form.get('email', '').strip()
#             password = request.form.get('password', '')
#
#             # ✅ اعتبارسنجی ورودی
#             if not username or not email or not password:
#                 flash("❌ تمام فیلدها الزامی هستند.", "error")
#                 return render_template('admin/create_first_admin.html')
#
#             if len(username) < 3:
#                 flash("❌ نام کاربری باید حداقل 3 کاراکتر باشد.", "error")
#                 return render_template('admin/create_first_admin.html')
#
#             if len(password) < 8:
#                 flash("❌ رمز عبور باید حداقل 8 کاراکتر باشد.", "error")
#                 return render_template('admin/create_first_admin.html')
#
#             # ✅ بررسی تکراری بودن
#             if User.query.filter_by(username=username, is_active=True).first():
#                 flash("❌ نام کاربری قبلاً گرفته شده.", "error")
#                 return render_template('admin/create_first_admin.html')
#
#             if User.query.filter_by(email=email, is_active=True).first():
#                 flash("❌ ایمیل قبلاً استفاده شده.", "error")
#                 return render_template('admin/create_first_admin.html')
#
#             # ✅ ایجاد ادمین
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
#             flash("✅ ادمین اول با موفقیت ایجاد شد.", "success")
#             return redirect(url_for('admin.login'))
#
#         except Exception as e:
#             db.session.rollback()
#             flash("❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.", "error")
#             current_app.logger.error(f"Error creating first admin: {e}")
#             return render_template('admin/create_first_admin.html')
#
#     # GET: نمایش فرم
#     return render_template('admin/create_first_admin.html')
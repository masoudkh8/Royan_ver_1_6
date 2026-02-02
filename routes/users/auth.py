
import random
import os
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_mail import Message
from models import db
from models.premium_request import PremiumRequest
from . import users_bp
from datetime import datetime
import pytz
tehran_tz = pytz.timezone('Asia/Tehran')

from flask import current_app
from extensions import mail
from kavenegar import *


# سریالایزر برای توکن ایمیل
def get_serializer():

    return URLSafeTimedSerializer(current_app.secret_key)


# # ارسال کد تأیید به موبایل (با Kavenegar)
# import requests
# import json
#
# def send_sms(phone, message):
#     api_key = "YOUR_API_KEY_HERE"  # ← کلید API خودت رو اینجا وارد کن
#     url = "https://api.kavenegar.com/v1/{}/sms/send.json".format(api_key)
#
#     # فرمت شماره باید ۱۰ رقمی و بدون صفر اول باشد (مثلاً 9123456789)
#     if phone.startswith("0"):
#         phone = phone[1:]
#
#     payload = {
#         "receptor": phone,
#         "message": message
#     }
#
#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded"
#     }
#
#     try:
#         response = requests.post(url, data=payload, headers=headers)
#         if response.status_code == 200:
#             result = response.json()
#             if result.get("return", {}).get("status") == 200:
#                 print(f"✅ پیامک به {phone} با موفقیت ارسال شد.")
#                 return True
#             else:
#                 print(f"❌ خطا در ارسال به {phone}: {result.get('return').get('message')}")
#                 return False
#         else:
#             print(f"❌ وضعیت پاسخ نامعتبر: {response.status_code}")
#             return False
#     except Exception as e:
#         print(f"❌ خطا در ارسال پیامک: {e}")
#         return False
#
#
# import requests
# from flask import current_app
#
# def send_sms(phone, message):
#     print("send sms function")
#     if not phone:
#         current_app.logger.error("شماره موبایل خالی است.")
#         return False
#
#     if current_app.config.get('DEBUG'):
#         current_app.logger.info(f"📤 [TEST] پیامک به {phone}: {message}")
#         return True  # فرض کن ارسال شد
#
#     api_key = current_app.config['KAVENEGAR_API_KEY']
#     url = f"https://api.kavenegar.com/v1/{api_key}/sms/send.json"
#
#     # فرمت شماره: حذف صفر اول
#     if phone.startswith("0"):
#         phone = phone[1:]
#
#     payload = {
#         "receptor": phone,
#         "message": message
#     }
#
#     try:
#         response = requests.post(url, data=payload)
#         if response.status_code == 200:
#             json_resp = response.json()
#             if json_resp["return"]["status"] == 200:
#                 current_app.logger.info(f"✅ پیامک به {phone} ارسال شد.")
#                 return True
#             else:
#                 current_app.logger.error(f"کاوه‌نگار خطا داد: {json_resp['return']['message']}")
#                 return False
#         else:
#             current_app.logger.error(f"خطای HTTP: {response.status_code}")
#             return False
#     except Exception as e:
#         current_app.logger.error(f"خطا در ارسال پیامک: {e}")
#         return False
#
# import requests
# from flask import current_app
# def send_sms(phone, message):
#     if not phone:
#         current_app.logger.error("شماره موبایل خالی است.")
#         return False
#
#     # حذف صفر اول
#     if phone.startswith("0"):
#         phone = phone[1:]
#
#     # تنظیمات AmootSMS
#     TOKEN = current_app.config["AMOOTSMS_TOKEN"]
#     url = "https://portal.amootsms.com/rest/SendSimple"
#     headers = {"Authorization": TOKEN}
#     data = {
#         "SMSMessageText": "message",
#         "LineNumber": "public",
#         "Mobiles": '09178001811',
#         "SendDateTime":datetime.now()
#     }
#     print(TOKEN,url,data)
#
#     try:
#         response = requests.post(url, data=data, headers=headers, timeout=50)
#         current_app.logger.info(f"وضعیت پاسخ: {response.status_code}")
#         current_app.logger.info(f"متن پاسخ: {response.text}")  # مهم: ببین چه چیزی برگشت
#
#         if response.status_code == 200:
#             try:
#                 json_resp = response.json()
#                 if json_resp.get("Status") == 200:
#                     return True
#                 else:
#                     error_msg = json_resp.get("Message", "No message in response")
#                     current_app.logger.error(f"❌ AmootSMS خطا داد: {error_msg}")
#             except Exception as e:
#                 current_app.logger.error(f"❌ پاسخ JSON نامعتبر: {response.text[:500]}")
#         else:
#             current_app.logger.error(f"❌ وضعیت HTTP ناموفق: {response.status_code}")
#
#     except requests.exceptions.Timeout:
#         current_app.logger.error("❌ درخواست به AmootSMS تایم‌اوت خورد.")
#     except requests.exceptions.ConnectionError:
#         current_app.logger.error("❌ مشکل در اتصال به سرور AmootSMS (اتصال قطع یا فیلتر).")
#     except Exception as e:
#         current_app.logger.error(f"❌ خطای کلی در ارسال پیامک: {e}")

import requests
# from urllib.parse import urlencode
# def send_sms(phone, message):
#     # ————————— تنظیمات —————————
#     TOKEN = "052877AF60F77DE6FA1E58D0761A339C5D8C6BAA"  # توکن شخصی شما در AmootSMS
#     MESSAGE = "پیامک تستی از پایتون"
#     LINE_NUMBER = "public"  # یا شماره اختصاصی شما
#     MOBILES = "9178001811"  # شماره مقصد — بدون صفر اول
#     SEND_DATE_TIME = '2025-09-09 04:50:00'  # خالی = ارسال فوری | فرمت پیشنهادی: "2025/08/15 14:30:00"
#
#     # ————————— آدرس API —————————
#     url = "https://portal.amootsms.com/rest/SendSimple"
#
#     # ————————— داده‌ها به فرمت فرم —————————
#     data = {
#         'SMSMessageText': MESSAGE,
#         'LineNumber': LINE_NUMBER,
#         'Mobiles': MOBILES
#
#     }
#
#     # فقط اگر بخواهی با تأخیر ارسال کنی
#     if SEND_DATE_TIME:
#         data['SendDateTime'] = '2025-09-09 04:50:00'
#
#     # ————————— هدرها —————————
#     headers = {
#         'Authorization': TOKEN,
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#
#     try:
#         # ارسال درخواست POST
#         response = requests.post(url, data=data, headers=headers, timeout=10)
#
#         # چاپ وضعیت و پاسخ
#         print(f"وضعیت پاسخ: {response.status_code}")
#
#         try:
#             json_resp = response.json()
#             print(f"پاسخ سرور: {json_resp}")
#
#             if json_resp.get("Status") in ["OK", "Submitted"] or json_resp.get("CampaignID", 0) > 0:
#                 print("✅ پیامک با موفقیت ارسال شد.")
#             else:
#                 print(f"❌ خطا: {json_resp.get('Status', 'Unknown error')}")
#         except Exception as e:
#             print(f"❌ پاسخ JSON نامعتبر: {response.text}")
#
#     except requests.exceptions.Timeout:
#         print("❌ درخواست به سرور زمان‌بندی شد (Timeout).")
#     except requests.exceptions.ConnectionError:
#         print("❌ مشکل در اتصال به سرور (ممکن است فیلتر باشد یا سرور خاموش).")
#     except Exception as e:
#         print(f"❌ خطای غیرمنتظره: {e}")
#



    #
    # try:
    #     response = requests.post(url, data=data, headers=headers)
    #     if response.status_code == 200:
    #         json_resp = response.json()
    #         if json_resp.get("Status") == 200:
    #             current_app.logger.info(f"✅ پیامک به {phone} ارسال شد.")
    #             return True
    #         else:
    #             current_app.logger.error(f"❌ AmootSMS خطا داد: {json_resp.get('Message')}")
    #     else:
    #         current_app.logger.error(f"❌ وضعیت HTTP: {response.status_code}")
    # except Exception as e:
    #     current_app.logger.error(f"❌ خطا در ارسال پیامک: {e}")
    #
    # return False
def send_sms(phone, message):
    print("0")
    print(current_app.config['KAVENEGAR_API_KEY'])
    print(current_app.config['D_STATE'])
    if not phone:
        print("00")
        current_app.logger.error("شماره موبایل خالی است.")
        return False

    # حذف صفر اول و بررسی فرمت
    cleaned_phone = phone
    if cleaned_phone.startswith("0"):
        cleaned_phone = cleaned_phone[1:]
        print("0d0")
    if not cleaned_phone.isdigit() or len(cleaned_phone) != 10:
        current_app.logger.error(f"فرمت شماره نامعتبر: {phone}")
        print("0e0")
        return False

    # حالت دیباگ: فقط لاگ بزن
   # "" if current_app.config.get('DEBUG'):
    if current_app.config['D_STATE']==1:
        print("0220")
        print(current_app.config.get('DEBUG'))
        current_app.logger.info(f"📤 [TEST] پیامک به {phone}: {message}")
        return True

    # حالت تولید: ارسال واقعی
    try:

        api = KavenegarAPI('5051786848506C45767269315634507077694A3157474E554B4E47775156385579774A38674E59587439633D')

        print(api)
        print(type('09178001811'))
        params = {'sender': '2000660110', 'receptor': phone, 'message': message}

        response = api.sms_send(params)

        print(response.status_code)
        if response.status_code == 200:
            json_resp = response.json()
            if json_resp["return"]["status"] == 200:
                current_app.logger.info(f"✅ پیامک به {phone} ارسال شد.")
                return True
            else:
                current_app.logger.error(f"کاوه‌نگار خطا داد: {json_resp['return']['message']}")
                return False
        else:
            current_app.logger.error(f"خطای HTTP: {response.status_code}, پاسخ: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print("1")
        current_app.logger.error(f"خطا در درخواست شبکه: {e}")
        return False
    except Exception as e:
        print("2")
        current_app.logger.error(f"خطا در ارسال پیامک: {e}")
        return False




# -------------------------------
# تأیید شماره موبایل
# -------------------------------
# @users_bp.route('/verify_phone', methods=['GET', 'POST'])
# @login_required
# def verify_phone():
#     req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()
#     print(req,"req")
#     if not req:
#         return redirect(url_for('users.upgrade_to_premium'))
#
#     if request.method == 'POST':
#         code = request.form['code']
#         print(req.phone_verification_code)
#         if code == req.phone_verification_code and req.phone_verification_code is not None:
#             req.phone_verified = True
#             db.session.commit()
#             flash("✅ شماره موبایل تأیید شد.")
#             return redirect(url_for('users.verify_phone'))
#         else:
#             flash("کد نامعتبر است.")
#
#     # ارسال کد
#     if not req.phone_verification_code:
#         print("PROVIDE CODE")
#         code = str(random.randint(100000, 999999))
#         req.phone_verification_code = code
#         db.session.commit()
#         send_sms(current_user.phone, f"کد تأیید شما: {code}")
#
#     return render_template('users/verify_phone.html', req=req)


#
# @users_bp.route('/verify_phone', methods=['GET', 'POST'])
# @login_required
# def verify_phone():
#     req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()
#     print(req,"req")
#     # اگر درخواستی نداشت، یکی بساز
#     if not req:
#         req = PremiumRequest(
#             user_id=current_user.id,
#             requested_phone = current_user.phone,
#             status='pending',
#             submitted_at=datetime.utcnow()
#         )
#         db.session.add(req)
#         db.session.commit()
#
#     # حالا req وجود دارد، ادامه منطق تأیید کد
#     if req.phone_verified:
#         flash("✅ شماره موبایل شما قبلاً تأیید شده است.")
#         return redirect(url_for('users.profile'))
#
#     if request.method == 'POST':
#         code = request.form.get('code', '').strip()
#         print(code,"code")
#         print(req.phone_verification_code, "req.phone_verification_code")
#         if not code:
#             flash("لطفاً کد را وارد کنید.")
#         elif code == req.phone_verification_code:
#             print(req.phone_verification_code, "req.phone_verification_code")
#             req.phone_verified = True
#             req.phone_verification_code = None
#             db.session.commit()
#             flash("✅ شماره موبایل تأیید شد.")
#             return redirect(url_for('users.payment_confirmation'))
#         else:
#             flash("کد نامعتبر است.")
#
#     # ارسال کد (اگر قبلاً ارسال نشده باشد)
#     if not req.phone_verification_code:
#         print(req.phone_verification_code, "creation")
#         code = str(random.randint(100000, 999999))
#         req.phone_verification_code = code
#         db.session.commit()
#         try:
#             send_sms(current_user.phone, f"کد تأیید: {code}")
#             flash("کد تأیید ارسال شد.")
#         except Exception as e:
#             flash("ارسال کد با مشکل مواجه شد.")
#             current_app.logger.error(f"SMS failed: {e}")
#
#     return render_template('users/verify_phone.html', req=req)



#پایینی اوکیه فقط pending میره
# @users_bp.route('/verify_phone', methods=['GET', 'POST'])
# @login_required
# def verify_phone():
#     if not current_user.phone or not current_user.phone.strip():
#         flash("❌ لطفاً ابتدا شماره موبایل خود را در پروفایل خود وارد کنید.")
#         return redirect(url_for('users.profile'))  # یا صفحه ویرایش پروفایل
#
#     req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()
#
#     if not req:
#         req = PremiumRequest(
#             user_id=current_user.id,
#             requested_phone=current_user.phone,
#             submitted_at=datetime.utcnow()
#         )
#         db.session.add(req)
#         db.session.commit()
#
#     if req.phone_verified:
#         flash("✅ شماره موبایل شما قبلاً تأیید شده است.")
#         return redirect(url_for('users.profile'))
#
#     if request.method == 'POST':
#         # بررسی ارسال مجدد کد
#         if 'resend' in request.form:
#             # حذف کد قبلی
#             code = str(random.randint(100000, 999999))
#             req.phone_verification_code = code
#             db.session.commit()
#             try:
#                 print("send_sms_function")
#                 send_sms(current_user.phone, f"کد تأیید: {code}")
#                 flash("کد جدید ارسال شد.")
#             except Exception as e:
#                 current_app.logger.error(f"SMS failed: {e}")
#                 flash("❌ ارسال کد با مشکل مواجه شد.")
#             return redirect(url_for('users.verify_phone'))
#
#         # بررسی تأیید کد
#         code = request.form.get('code', '').strip()
#         if not code:
#             flash("لطفاً کد را وارد کنید.")
#         elif code == req.phone_verification_code:
#             req.phone_verified = True
#             req.phone_verification_code = None
#             db.session.commit()
#             flash("✅ شماره موبایل با موفقیت تأیید شد.")
#             return redirect(url_for('users.payment_confirmation'))
#         else:
#             flash("❌ کد نامعتبر است.")
#
#     # ارسال اولیه کد (اگر قبلاً ارسال نشده باشد)
#     if not req.phone_verification_code:
#         code = str(random.randint(100000, 999999))
#         req.phone_verification_code = code
#         db.session.commit()
#         try:
#             send_sms(current_user.phone, f"کد تأیید: {code}")
#             flash("کد تأیید به شماره شما ارسال شد.")
#         except Exception as e:
#             current_app.logger.error(f"SMS failed: {e}")
#             flash("❌ ارسال کد با مشکل مواجه شد.")
#
#     return render_template('users/verify_phone.html', req=req)

@users_bp.route('/verify_phone', methods=['GET', 'POST'])
@login_required
def verify_phone():
    if not current_user.phone or not current_user.phone.strip():
        flash("❌ لطفاً ابتدا شماره موبایل خود را در پروفایل خود وارد کنید.")
        return redirect(url_for('users.profile'))

    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()

    # اگر درخواستی وجود ندارد، یک درخواست جدید با وضعیت draft ایجاد کن
    if not req:
        req = PremiumRequest(
            user_id=current_user.id,
            requested_phone=current_user.phone,
            status='draft',  # ✅ تغییر از 'pending' به 'draft'
            submitted_at=datetime.now(tehran_tz)
        )
        db.session.add(req)
        db.session.commit()

    # اگر شماره قبلاً تأیید شده، به مرحله بعد برو
    if req.phone_verified:
        flash("✅ شماره موبایل شما قبلاً تأیید شده است.")
        return redirect(url_for('users.verify_email'))  # ✅ به ایمیل برو، نه payment_confirmation

    if request.method == 'POST':
        if 'resend' in request.form:
            code = str(random.randint(100000, 999999))
            req.phone_verification_code = code
            db.session.commit()
            try:
                send_sms(current_user.phone, f"کد تأیید: {code}")
                flash("کد جدید ارسال شد.")
            except Exception as e:
                current_app.logger.error(f"SMS failed: {e}")
                flash("❌ ارسال کد با مشکل مواجه شد.")
            return redirect(url_for('users.verify_phone'))

        code = request.form.get('code', '').strip()
        if not code:
            flash("لطفاً کد را وارد کنید.")
        elif code == req.phone_verification_code:
            req.phone_verified = True
            req.phone_verification_code = None
            db.session.commit()
            flash("✅ شماره موبایل با موفقیت تأیید شد.")
            return redirect(url_for('users.verify_email'))  # ✅ بعد از تأیید شماره، به ایمیل برو
        else:
            flash("❌ کد نامعتبر است.")

    # ارسال اولیه کد
    if not req.phone_verification_code:
        code = str(random.randint(100000, 999999))
        req.phone_verification_code = code
        db.session.commit()
        try:
            send_sms(current_user.phone, f"کد تأیید: {code}")
            flash("کد تأیید به شماره شما ارسال شد.")
        except Exception as e:
            current_app.logger.error(f"SMS failed: {e}")
            flash("❌ ارسال کد با مشکل مواجه شد.")

    return render_template('users/verify_phone.html', req=req)







# -------------------------------
# تأیید ایمیل (صفحه نمایش)
# -------------------------------
@users_bp.route('/verify_email')
@login_required
def verify_email():
    print('start email process')
    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()
    # if not req:
    #     print('if not req')
    #     return redirect(url_for('users.upgrade_to_premium'))

    if not req or not req.phone_verified:
        return redirect(url_for('users.verify_phone'))


    if req.email_verified:
        print('req.email_verified')
        return redirect(url_for('users.upload_documents'))

    # if req.email_verification_token:
    #     print(req.email_verification_token)

    if not req.email_verification_token:
        # print('not req.email_verification_token')
        if send_email_verification(current_user):
            # print('....... send_email_verification')
            flash("ایمیل تأیید ارسال شد.")
        else:
            print('....... ❌❌')
            flash("❌ ارسال ایمیل با خطا مواجه شد.")
            return render_template('users/verify_email.html', req=req)

    return render_template('users/verify_email.html', req=req)


# ارسال ایمیل تأیید
def send_email_verification(user):

    print('send email func')
    serializer = get_serializer()
    token = serializer.dumps(user.email, salt='email-verify-salt')

    req = PremiumRequest.query.filter_by(user_id=user.id).order_by(PremiumRequest.submitted_at.desc()).first()
    print(req)
    if req:
        req.email_verification_token = token
        db.session.commit()

    confirm_url = url_for('users.confirm_email', token=token, _external=True)

    html_body = f"""
    <h2>سلام {user.username}!</h2>
    <p>برای تکمیل فرآیند ارتقاء به کاربر ویژه، ایمیل خود را تأیید کنید:</p>
    <p><a href="{confirm_url}">✅ تأیید ایمیل</a></p>
    <p>این لینک پس از 24 ساعت منقضی می‌شود.</p>
    """

    msg = Message(
        subject="✅ تأیید ایمیل - فرآیند ارتقاء",
        recipients=[user.email],
        html=html_body,
        sender=current_app.config.get('MAIL_DEFAULT_SENDER')
    )
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"❌ خطا در ارسال ایمیل: {e}")
        return False


# -------------------------------
# تأیید توکن ایمیل
# -------------------------------
@users_bp.route('/confirm_email/<token>')
@login_required
def confirm_email(token):
    print('start confirm_email func')
    s = get_serializer()
    try:
        email = s.loads(token, salt='email-verify-salt', max_age=86400)
    except SignatureExpired:
        flash("❌ لینک منقضی شده است.")
        return redirect(url_for('users.verify_email'))
    except BadSignature:
        flash("❌ لینک نامعتبر است.")
        return redirect(url_for('users.upgrade_to_premium'))

    if email != current_user.email:
        flash("❌ این لینک برای شما نیست.")
        return redirect(url_for('users.login'))

    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()
    if not req:
        flash("❌ درخواستی یافت نشد.")
        return redirect(url_for('users.upgrade_to_premium'))

    if not req.email_verified:
        req.email_verified = True
        req.email_verification_token = None
        db.session.commit()
        flash("✅ ایمیل تأیید شد.")

    return redirect(url_for('users.upload_documents'))
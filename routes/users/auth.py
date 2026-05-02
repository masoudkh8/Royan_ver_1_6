
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


# سریالایزر برای توکن Email
def get_serializer():

    return URLSafeTimedSerializer(current_app.secret_key)


# # Send کد تأیید to موبایل (با Kavenegar)
# import requests
# import json
#
# def send_sms(phone, message):
#     api_key = "YOUR_API_KEY_HERE"  # ← کلید API خودت رو اینجا واReject کن
#     url = "https://api.kavenegar.com/v1/{}/sms/send.json".format(api_key)
#
#     # فرمت شماره باید 10 رقمی و بدون صفر اول باشد (مثلاً 9123456789)
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
#                 print(f"✅ Messageک to {phone} successfully Send شد.")
#                 return True
#             else:
#                 print(f"❌ Error در Send to {phone}: {result.get('return').get('message')}")
#                 return False
#         else:
#             print(f"❌ Status پاسخ نامعتبر: {response.status_code}")
#             return False
#     except Exception as e:
#         print(f"❌ Error در Send Messageک: {e}")
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
#         current_app.logger.info(f"📤 [TEST] Messageک to {phone}: {message}")
#         return True  # فرض کن Send شد
#
#     api_key = current_app.config['KAVENEGAR_API_KEY']
#     url = f"https://api.kavenegar.com/v1/{api_key}/sms/send.json"
#
#     # فرمت شماره: Delete صفر اول
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
#                 current_app.logger.info(f"✅ Messageک to {phone} Send شد.")
#                 return True
#             else:
#                 current_app.logger.error(f"کاوه‌نگار Error داد: {json_resp['return']['message']}")
#                 return False
#         else:
#             current_app.logger.error(f"Errorی HTTP: {response.status_code}")
#             return False
#     except Exception as e:
#         current_app.logger.error(f"Error در Send Messageک: {e}")
#         return False
#
# import requests
# from flask import current_app
# def send_sms(phone, message):
#     if not phone:
#         current_app.logger.error("شماره موبایل خالی است.")
#         return False
#
#     # Delete صفر اول
#     if phone.startswith("0"):
#         phone = phone[1:]
#
#     # Settings AmootSMS
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
#         current_app.logger.info(f"Status پاسخ: {response.status_code}")
#         current_app.logger.info(f"مTon پاسخ: {response.text}")  # Important: ببین چه چیزی برگشت
#
#         if response.status_code == 200:
#             try:
#                 json_resp = response.json()
#                 if json_resp.get("Status") == 200:
#                     return True
#                 else:
#                     error_msg = json_resp.get("Message", "No message in response")
#                     current_app.logger.error(f"❌ AmootSMS Error داد: {error_msg}")
#             except Exception as e:
#                 current_app.logger.error(f"❌ پاسخ JSON نامعتبر: {response.text[:500]}")
#         else:
#             current_app.logger.error(f"❌ Status HTTP ناموفق: {response.status_code}")
#
#     except requests.exceptions.Timeout:
#         current_app.logger.error("❌ درخواست to AmootSMS تایم‌اوت خوReject.")
#     except requests.exceptions.ConnectionError:
#         current_app.logger.error("❌ مشکل در اتصال to سرور AmootSMS (اتصال قطع یا Filter).")
#     except Exception as e:
#         current_app.logger.error(f"❌ Errorی کلی در Send Messageک: {e}")

import requests
# from urllib.parse import urlencode
# def send_sms(phone, message):
#     # ————————— Settings —————————
#     TOKEN = "052877AF60F77DE6FA1E58D0761A339C5D8C6BAA"  # توکن شخصی شما در AmootSMS
#     MESSAGE = "Messageک تستی از پایتون"
#     LINE_NUMBER = "public"  # یا شماره اختصاصی شما
#     MOBILES = "9178001811"  # شماره Destination — بدون صفر اول
#     SEND_DATE_TIME = '2025-09-09 04:50:00'  # خالی = Send Urgent | فرمت پیشنهادی: "2025/08/15 14:30:00"
#
#     # ————————— آدرس API —————————
#     url = "https://portal.amootsms.com/rest/SendSimple"
#
#     # ————————— داده‌ها to فرمت فرم —————————
#     data = {
#         'SMSMessageText': MESSAGE,
#         'LineNumber': LINE_NUMBER,
#         'Mobiles': MOBILES
#
#     }
#
#     # فقط اگر بخواهی با تأNo Send کنی
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
#         # Send درخواست POST
#         response = requests.post(url, data=data, headers=headers, timeout=10)
#
#         # چاپ Status و پاسخ
#         print(f"Status پاسخ: {response.status_code}")
#
#         try:
#             json_resp = response.json()
#             print(f"پاسخ سرور: {json_resp}")
#
#             if json_resp.get("Status") in ["OK", "Submitted"] or json_resp.get("CampaignID", 0) > 0:
#                 print("✅ Messageک successfully Send شد.")
#             else:
#                 print(f"❌ Error: {json_resp.get('Status', 'Unknown error')}")
#         except Exception as e:
#             print(f"❌ پاسخ JSON نامعتبر: {response.text}")
#
#     except requests.exceptions.Timeout:
#         print("❌ درخواست to سرور زمان‌بندی شد (Timeout).")
#     except requests.exceptions.ConnectionError:
#         print("❌ مشکل در اتصال to سرور (ممکن است Filter باشد یا سرور خاموش).")
#     except Exception as e:
#         print(f"❌ Errorی غیرمنتظره: {e}")
#



    #
    # try:
    #     response = requests.post(url, data=data, headers=headers)
    #     if response.status_code == 200:
    #         json_resp = response.json()
    #         if json_resp.get("Status") == 200:
    #             current_app.logger.info(f"✅ Messageک to {phone} Send شد.")
    #             return True
    #         else:
    #             current_app.logger.error(f"❌ AmootSMS Error داد: {json_resp.get('Message')}")
    #     else:
    #         current_app.logger.error(f"❌ Status HTTP: {response.status_code}")
    # except Exception as e:
    #     current_app.logger.error(f"❌ Error در Send Messageک: {e}")
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

    # Delete صفر اول و بررسی فرمت
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
        current_app.logger.info(f"📤 [TEST] Messageک to {phone}: {message}")
        return True

    # حالت تولید: Send واقعی
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
                current_app.logger.info(f"✅ Messageک to {phone} Send شد.")
                return True
            else:
                current_app.logger.error(f"کاوه‌نگار Error داد: {json_resp['return']['message']}")
                return False
        else:
            current_app.logger.error(f"Errorی HTTP: {response.status_code}, پاسخ: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print("1")
        current_app.logger.error(f"Error در درخواست شبکه: {e}")
        return False
    except Exception as e:
        print("2")
        current_app.logger.error(f"Error در Send Messageک: {e}")
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
#     # Send کد
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
#     # حالا req وجود داReject، ادامه منطق تأیید کد
#     if req.phone_verified:
#         flash("✅ شماره موبایل شما قبلاً تأیید شده است.")
#         return redirect(url_for('users.profile'))
#
#     if request.method == 'POST':
#         code = request.form.get('code', '').strip()
#         print(code,"code")
#         print(req.phone_verification_code, "req.phone_verification_code")
#         if not code:
#             flash("لطفاً کد را واReject کنید.")
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
#     # Send کد (اگر قبلاً Send نشده باشد)
#     if not req.phone_verification_code:
#         print(req.phone_verification_code, "creation")
#         code = str(random.randint(100000, 999999))
#         req.phone_verification_code = code
#         db.session.commit()
#         try:
#             send_sms(current_user.phone, f"کد تأیید: {code}")
#             flash("کد تأیید Send شد.")
#         except Exception as e:
#             flash("Send کد با مشکل مواجه شد.")
#             current_app.logger.error(f"SMS failed: {e}")
#
#     return render_template('users/verify_phone.html', req=req)



#Bottomی اوکیه فقط pending میره
# @users_bp.route('/verify_phone', methods=['GET', 'POST'])
# @login_required
# def verify_phone():
#     if not current_user.phone or not current_user.phone.strip():
#         flash("❌ لطفاً ابتدا شماره موبایل خود را در Profile خود واReject کنید.")
#         return redirect(url_for('users.profile'))  # یا صفحه Edit Profile
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
#         # بررسی Send مجدد کد
#         if 'resend' in request.form:
#             # Delete کد Previous
#             code = str(random.randint(100000, 999999))
#             req.phone_verification_code = code
#             db.session.commit()
#             try:
#                 print("send_sms_function")
#                 send_sms(current_user.phone, f"کد تأیید: {code}")
#                 flash("کد New Send شد.")
#             except Exception as e:
#                 current_app.logger.error(f"SMS failed: {e}")
#                 flash("❌ Send کد با مشکل مواجه شد.")
#             return redirect(url_for('users.verify_phone'))
#
#         # بررسی تأیید کد
#         code = request.form.get('code', '').strip()
#         if not code:
#             flash("لطفاً کد را واReject کنید.")
#         elif code == req.phone_verification_code:
#             req.phone_verified = True
#             req.phone_verification_code = None
#             db.session.commit()
#             flash("✅ شماره موبایل successfully تأیید شد.")
#             return redirect(url_for('users.payment_confirmation'))
#         else:
#             flash("❌ کد نامعتبر است.")
#
#     # Send اولیه کد (اگر قبلاً Send نشده باشد)
#     if not req.phone_verification_code:
#         code = str(random.randint(100000, 999999))
#         req.phone_verification_code = code
#         db.session.commit()
#         try:
#             send_sms(current_user.phone, f"کد تأیید: {code}")
#             flash("کد تأیید to شماره شما Send شد.")
#         except Exception as e:
#             current_app.logger.error(f"SMS failed: {e}")
#             flash("❌ Send کد با مشکل مواجه شد.")
#
#     return render_template('users/verify_phone.html', req=req)

@users_bp.route('/verify_phone', methods=['GET', 'POST'])
@login_required
def verify_phone():
    if not current_user.phone or not current_user.phone.strip():
        flash("❌ لطفاً ابتدا شماره موبایل خود را در Profile خود واReject کنید.")
        return redirect(url_for('users.profile'))

    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()

    # اگر درخواستی وجود نداReject، یک درخواست New با Status draft ایجاد کن
    if not req:
        req = PremiumRequest(
            user_id=current_user.id,
            requested_phone=current_user.phone,
            status='draft',  # ✅ تغییر از 'pending' to 'draft'
            submitted_at=datetime.now(tehran_tz)
        )
        db.session.add(req)
        db.session.commit()

    # اگر شماره قبلاً تأیید شده، to مرحله بعد برو
    if req.phone_verified:
        flash("✅ شماره موبایل شما قبلاً تأیید شده است.")
        return redirect(url_for('users.verify_email'))  # ✅ to Email برو، نه payment_confirmation

    if request.method == 'POST':
        if 'resend' in request.form:
            code = str(random.randint(100000, 999999))
            req.phone_verification_code = code
            db.session.commit()
            try:
                send_sms(current_user.phone, f"کد تأیید: {code}")
                flash("کد New Send شد.")
            except Exception as e:
                current_app.logger.error(f"SMS failed: {e}")
                flash("❌ Send کد با مشکل مواجه شد.")
            return redirect(url_for('users.verify_phone'))

        code = request.form.get('code', '').strip()
        if not code:
            flash("لطفاً کد را واReject کنید.")
        elif code == req.phone_verification_code:
            req.phone_verified = True
            req.phone_verification_code = None
            db.session.commit()
            flash("✅ شماره موبایل successfully تأیید شد.")
            return redirect(url_for('users.verify_email'))  # ✅ بعد از تأیید شماره، to Email برو
        else:
            flash("❌ کد نامعتبر است.")

    # Send اولیه کد
    if not req.phone_verification_code:
        code = str(random.randint(100000, 999999))
        req.phone_verification_code = code
        db.session.commit()
        try:
            send_sms(current_user.phone, f"کد تأیید: {code}")
            flash("کد تأیید to شماره شما Send شد.")
        except Exception as e:
            current_app.logger.error(f"SMS failed: {e}")
            flash("❌ Send کد با مشکل مواجه شد.")

    return render_template('users/verify_phone.html', req=req)







# -------------------------------
# تأیید Email (صفحه Show)
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
            flash("Email تأیید Send شد.")
        else:
            print('....... ❌❌')
            flash("❌ Send Email با Error مواجه شد.")
            return render_template('users/verify_email.html', req=req)

    return render_template('users/verify_email.html', req=req)


# Send Email تأیید
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
    <p>برای تکمیل فرآیند ارتقاء to Premium User، Email خود را تأیید کنید:</p>
    <p><a href="{confirm_url}">✅ تأیید Email</a></p>
    <p>این لینک پس از 24 ساعت منقضی می‌شود.</p>
    """

    msg = Message(
        subject="✅ تأیید Email - فرآیند ارتقاء",
        recipients=[user.email],
        html=html_body,
        sender=current_app.config.get('MAIL_DEFAULT_SENDER')
    )
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"❌ Error در Send Email: {e}")
        return False


# -------------------------------
# تأیید توکن Email
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
        flash("✅ Email تأیید شد.")

    return redirect(url_for('users.upload_documents'))
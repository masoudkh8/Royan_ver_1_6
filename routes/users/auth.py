
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


# سریالایزر برای token Email
def get_serializer():

    return URLSafeTimedSerializer(current_app.secret_key)


# # Send verification code to mobile (via Kavenegar)
# import requests
# import json
#
# def send_sms(phone, message):
#     api_key = "YOUR_API_KEY_HERE"  # ← api key خودت رو اینجا واReject کن
#     url = "https://api.kavenegar.com/v1/{}/sms/send.json".format(api_key)
#
#     # Phone number must be 10 digits without leading zero (مثلاً 9123456789)
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
#             print(f"❌ Status response Invalid: {response.status_code}")
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
#         current_app.logger.error("mobile number empty است.")
#         return False
#
#     if current_app.config.get('DEBUG'):
#         current_app.logger.info(f"📤 [TEST] Messageک to {phone}: {message}")
#         return True  # فرض کن Send شد
#
#     api_key = current_app.config['KAVENEGAR_API_KEY']
#     url = f"https://api.kavenegar.com/v1/{api_key}/sms/send.json"
#
#     # Phone format: Remove leading zero
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
#         current_app.logger.error("mobile number empty است.")
#         return False
#
#     # Remove leading zero
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
#         current_app.logger.info(f"Status response: {response.status_code}")
#         current_app.logger.info(f"مTon response: {response.text}")  # Important: ببین چه چیزی back
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
#                 current_app.logger.error(f"❌ response JSON Invalid: {response.text[:500]}")
#         else:
#             current_app.logger.error(f"❌ Status HTTP ناSuccess: {response.status_code}")
#
#     except requests.exceptions.Timeout:
#         current_app.logger.error("❌ request to AmootSMS تایم‌اوت خوReject.")
#     except requests.exceptions.ConnectionError:
#         current_app.logger.error("❌ issue در connection to سرور AmootSMS (connection قطع یا Filter).")
#     except Exception as e:
#         current_app.logger.error(f"❌ Errorی کلی در Send Messageک: {e}")

import requests
# from urllib.parse import urlencode
# def send_sms(phone, message):
#     # ————————— Settings —————————
#     TOKEN = "052877AF60F77DE6FA1E58D0761A339C5D8C6BAA"  # Your personal token at AmootSMS
#     MESSAGE = "Messageک تستی of پایتون"
#     LINE_NUMBER = "public"  # یا شماره اختصاصی شما
#     MOBILES = "9178001811"  # شماره Destination — بدون صفر first
#     SEND_DATE_TIME = '2025-09-09 04:50:00'  # empty = Send Urgent | Suggested format: "2025/08/15 14:30:00"
#
#     # ————————— address API —————————
#     url = "https://portal.amootsms.com/rest/SendSimple"
#
#     # ————————— Data in form format —————————
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
#     # ————————— Headers —————————
#     headers = {
#         'Authorization': TOKEN,
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#
#     try:
#         # Send request POST
#         response = requests.post(url, data=data, headers=headers, timeout=10)
#
#         # چapp Status و response
#         print(f"Status response: {response.status_code}")
#
#         try:
#             json_resp = response.json()
#             print(f"response سرور: {json_resp}")
#
#             if json_resp.get("Status") in ["OK", "Submitted"] or json_resp.get("CampaignID", 0) > 0:
#                 print("✅ Messageک successfully Send شد.")
#             else:
#                 print(f"❌ Error: {json_resp.get('Status', 'Unknown error')}")
#         except Exception as e:
#             print(f"❌ response JSON Invalid: {response.text}")
#
#     except requests.exceptions.Timeout:
#         print("❌ Request timed out (Timeout).")
#     except requests.exceptions.ConnectionError:
#         print("❌ issue در connection to سرور (ممکن است Filter باشد یا سرور خاموش).")
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
        current_app.logger.error("mobile number empty است.")
        return False

    # Remove leading zero و بررسی Formت
    cleaned_phone = phone
    if cleaned_phone.startswith("0"):
        cleaned_phone = cleaned_phone[1:]
        print("0d0")
    if not cleaned_phone.isdigit() or len(cleaned_phone) != 10:
        current_app.logger.error(f"Formت شماره Invalid: {phone}")
        print("0e0")
        return False

    # حالت دیباگ: فقط log بfemale
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
            current_app.logger.error(f"Errorی HTTP: {response.status_code}, response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print("1")
        current_app.logger.error(f"Error در request nightکه: {e}")
        return False
    except Exception as e:
        print("2")
        current_app.logger.error(f"Error در Send Messageک: {e}")
        return False




# -------------------------------
# تأیید mobile number
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
#             flash("✅ Mobile number verified.")
#             return redirect(url_for('users.verify_phone'))
#         else:
#             flash("Invalid code.")
#
#     # Send code
#     if not req.phone_verification_code:
#         print("PROVIDE CODE")
#         code = str(random.randint(100000, 999999))
#         req.phone_verification_code = code
#         db.session.commit()
#         send_sms(current_user.phone, f"Verification code شما: {code}")
#
#     return render_template('users/verify_phone.html', req=req)


#
# @users_bp.route('/verify_phone', methods=['GET', 'POST'])
# @login_required
# def verify_phone():
#     req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()
#     print(req,"req")
#     # If no request exists, create one
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
#     # حالا req وجود داReject، Continue logic تأیید کد
#     if req.phone_verified:
#         flash("✅ Your mobile number is already confirmed.")
#         return redirect(url_for('users.profile'))
#
#     if request.method == 'POST':
#         code = request.form.get('code', '').strip()
#         print(code,"code")
#         print(req.phone_verification_code, "req.phone_verification_code")
#         if not code:
#             flash("Please verify the code.")
#         elif code == req.phone_verification_code:
#             print(req.phone_verification_code, "req.phone_verification_code")
#             req.phone_verified = True
#             req.phone_verification_code = None
#             db.session.commit()
#             flash("✅ Mobile number verified.")
#             return redirect(url_for('users.payment_confirmation'))
#         else:
#             flash("Invalid code.")
#
#     # Send code (if not already sent)
#     if not req.phone_verification_code:
#         print(req.phone_verification_code, "creation")
#         code = str(random.randint(100000, 999999))
#         req.phone_verification_code = code
#         db.session.commit()
#         try:
#             send_sms(current_user.phone, f"Verification code: {code}")
#             flash("Verification code sent.")
#         except Exception as e:
#             flash("Code sending encountered an issue.")
#             current_app.logger.error(f"SMS failed: {e}")
#
#     return render_template('users/verify_phone.html', req=req)



#Bottomی اوکیه فقط pending میره
# @users_bp.route('/verify_phone', methods=['GET', 'POST'])
# @login_required
# def verify_phone():
#     if not current_user.phone or not current_user.phone.strip():
#         flash("❌ Please first verify your mobile number in your profile.")
#         return redirect(url_for('users.profile'))  # یا page Edit Profile
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
#         flash("✅ Your mobile number is already confirmed.")
#         return redirect(url_for('users.profile'))
#
#     if request.method == 'POST':
#         # Check resend code
#         if 'resend' in request.form:
#             # Delete previous code
#             code = str(random.randint(100000, 999999))
#             req.phone_verification_code = code
#             db.session.commit()
#             try:
#                 print("send_sms_function")
#                 send_sms(current_user.phone, f"Verification code: {code}")
#                 flash("New code sent.")
#             except Exception as e:
#                 current_app.logger.error(f"SMS failed: {e}")
#                 flash("❌ Code sending encountered an issue.")
#             return redirect(url_for('users.verify_phone'))
#
#         # Check code verification
#         code = request.form.get('code', '').strip()
#         if not code:
#             flash("Please verify the code.")
#         elif code == req.phone_verification_code:
#             req.phone_verified = True
#             req.phone_verification_code = None
#             db.session.commit()
#             flash("✅ Mobile number successfully verified.")
#             return redirect(url_for('users.payment_confirmation'))
#         else:
#             flash("❌ Invalid code.")
#
#     # Send first code (if not already sent)
#     if not req.phone_verification_code:
#         code = str(random.randint(100000, 999999))
#         req.phone_verification_code = code
#         db.session.commit()
#         try:
#             send_sms(current_user.phone, f"Verification code: {code}")
#             flash("Verification code sent to your number.")
#         except Exception as e:
#             current_app.logger.error(f"SMS failed: {e}")
#             flash("❌ Code sending encountered an issue.")
#
#     return render_template('users/verify_phone.html', req=req)

@users_bp.route('/verify_phone', methods=['GET', 'POST'])
@login_required
def verify_phone():
    if not current_user.phone or not current_user.phone.strip():
        flash("❌ Please first verify your mobile number in your profile.")
        return redirect(url_for('users.profile'))

    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()

    # اگر requestی وجود نداReject، یک request New با Status draft ایجاد کن
    if not req:
        req = PremiumRequest(
            user_id=current_user.id,
            requested_phone=current_user.phone,
            status='draft',  # ✅ change of 'pending' to 'draft'
            submitted_at=datetime.now(tehran_tz)
        )
        db.session.add(req)
        db.session.commit()

    # اگر شماره agoاً Confirmed، to مرحله later برو
    if req.phone_verified:
        flash("✅ Your mobile number is already confirmed.")
        return redirect(url_for('users.verify_email'))  # ✅ to Email برو، نه payment_confirmation

    if request.method == 'POST':
        if 'resend' in request.form:
            code = str(random.randint(100000, 999999))
            req.phone_verification_code = code
            db.session.commit()
            try:
                send_sms(current_user.phone, f"Verification code: {code}")
                flash("New code sent.")
            except Exception as e:
                current_app.logger.error(f"SMS failed: {e}")
                flash("❌ Code sending encountered an issue.")
            return redirect(url_for('users.verify_phone'))

        code = request.form.get('code', '').strip()
        if not code:
            flash("Please verify the code.")
        elif code == req.phone_verification_code:
            req.phone_verified = True
            req.phone_verification_code = None
            db.session.commit()
            flash("✅ Mobile number successfully verified.")
            return redirect(url_for('users.verify_email'))  # ✅ later of تأیید شماره، to Email برو
        else:
            flash("❌ Invalid code.")

    # Send firstیه کد
    if not req.phone_verification_code:
        code = str(random.randint(100000, 999999))
        req.phone_verification_code = code
        db.session.commit()
        try:
            send_sms(current_user.phone, f"Verification code: {code}")
            flash("Verification code sent to your number.")
        except Exception as e:
            current_app.logger.error(f"SMS failed: {e}")
            flash("❌ Code sending encountered an issue.")

    return render_template('users/verify_phone.html', req=req)







# -------------------------------
# Verify email (page Show)
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
            flash("Verification email sent.")
        else:
            print('....... ❌❌')
            flash("❌ Email sending encountered an error.")
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
    <h2>hello {user.username}!</h2>
    <p>برای تکمیل فرآیند upgrade to Premium User، Email خود را تأیید کنید:</p>
    <p><a href="{confirm_url}">✅ Verify email</a></p>
    <p>این لینک پس of 24 hour منقضی می‌شود.</p>
    """

    msg = Message(
        subject="✅ Verify email - فرآیند upgrade",
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
# تأیید token Email
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
        flash("❌ Invalid link.")
        return redirect(url_for('users.upgrade_to_premium'))

    if email != current_user.email:
        flash("❌ این لینک برای شما نیست.")
        return redirect(url_for('users.login'))

    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()
    if not req:
        flash("❌ Request not found.")
        return redirect(url_for('users.upgrade_to_premium'))

    if not req.email_verified:
        req.email_verified = True
        req.email_verification_token = None
        db.session.commit()
        flash("✅ Email verified.")

    return redirect(url_for('users.upload_documents'))
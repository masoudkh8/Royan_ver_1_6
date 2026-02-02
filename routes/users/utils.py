# routes/users/utils.py
from flask import url_for
from flask_mail import Message
from app import mail, get_serializer

def send_email_verification(user):
    s = get_serializer()
    token = s.dumps(user.email, salt='email-verify')

    verify_url = url_for('users.confirm_email', token=token, _external=True)

    html_body = f"""
    <h2>تبریک! درخواست ارتقاء به کاربر ویژه</h2>
    <p>برای تأیید آدرس ایمیل خود، روی لینک زیر کلیک کنید:</p>
    <p><a href="{verify_url}" style="color: #007BFF;">تأیید ایمیل</a></p>
    <p>این لینک پس از ۱ ساعت منقضی می‌شود.</p>
    <p>اگر شما این درخواست را نداده‌اید، این ایمیل را نادیده بگیرید.</p>
    """

    msg = Message(
        subject="تأیید ایمیل برای ارتقاء به کاربر ویژه",
        recipients=[user.email],
        html=html_body
    )
    mail.send(msg)
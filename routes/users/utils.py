# routes/users/utils.py
from flask import url_for
from flask_mail import Message
from app import mail, get_serializer

def send_email_verification(user):
    s = get_serializer()
    token = s.dumps(user.email, salt='email-verify')

    verify_url = url_for('users.confirm_email', token=token, _external=True)

    html_body = f"""
    <h2>تبریک! Upgrade request to Premium User</h2>
    <p>برای تأیید آدرس Email خود، Click the link below:</p>
    <p><a href="{verify_url}" style="color: #007BFF;">تأیید Email</a></p>
    <p>این لینک پس از 1 ساعت منقضی می‌شود.</p>
    <p>If you didn't request this, please ignore this email.</p>
    """

    msg = Message(
        subject="تأیید Email برای ارتقاء to Premium User",
        recipients=[user.email],
        html=html_body
    )
    mail.send(msg)
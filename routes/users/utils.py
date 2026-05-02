# routes/users/utils.py
from flask import url_for
from flask_mail import Message
from app import mail, get_serializer

def send_email_verification(user):
    s = get_serializer()
    token = s.dumps(user.email, salt='email-verify')

    verify_url = url_for('users.confirm_email', token=token, _external=True)

    html_body = f"""
    <h2>Congratulations! Upgrade request to Premium User</h2>
    <p>برای تأیید address Email خود، Click the link below:</p>
    <p><a href="{verify_url}" style="color: #007BFF;">Verify email</a></p>
    <p>این لینک پس of 1 hour منقضی می‌شود.</p>
    <p>If you didn't request this, please ignore this email.</p>
    """

    msg = Message(
        subject="Verify email برای upgrade to Premium User",
        recipients=[user.email],
        html=html_body
    )
    mail.send(msg)
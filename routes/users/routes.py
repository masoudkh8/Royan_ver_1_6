# routes/users/routes.py

from datetime import datetime
import pytz
tehran_tz = pytz.timezone('Asia/Tehran')

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from models import Message, Notification
from models.user import db, User, Role
from models.port import Port

from routes.users import users_bp,root_bp

# route change language
@root_bp.route('/set_language/<lang_code>')
def set_language(lang_code):
    """Change user language"""
    from app import SUPPORTED_LANGUAGES
    if lang_code in SUPPORTED_LANGUAGES:
        session['lang'] = lang_code
    # back to page Previous
    next_url = request.args.get('next', request.referrer or url_for('main_page'))
    return redirect(next_url)

# routes/users/routes.py یا app.py
@root_bp.route('/')
def main_page():
    return render_template('index.html')

@root_bp.route('/change_language/<lang_code>')
def change_language(lang_code):
    """Endpoint جایگزین برای change language - قابل دسترسی با name root.change_language"""
    return set_language(lang_code)


@users_bp.route('/create_first_admin', methods=['GET', 'POST'])
def create_first_admin():
    if User.query.filter_by(role='admin', is_active=True).first():
        flash("An admin already exists.")
        return redirect(url_for('users.login'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']


        if User.query.filter_by(username=username, is_active=True).first():
            flash("❌ Username already taken.")
            return redirect(url_for('users.register'))

        if User.query.filter_by(email=email, is_active=True).first():
            flash("❌ Email already in use.")
            return redirect(url_for('users.register'))

        hashed = generate_password_hash(password)
        user = User(
            username=username,
            email=email,
            password_hash=hashed,
            role=Role.ADMIN,
            is_premium=True
        )

        db.session.add(user)
        db.session.commit()
        flash("First Admin created.")
        return redirect(url_for('admin.login'))

    return '''
    <form method="post">
        <input name="username" placeholder="Username" required><br>
        <input name="email" type="email" placeholder="Email" required><br>
        <input name="password" type="password" placeholder="Password" required><br>
        <button type="submit">Create Admin</button>
    </form>
    '''

# -------------------------------
# Register
# -------------------------------
@users_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        company = request.form.get('company')
        country = request.form.get('country')
        phone = request.form.get('phone')

        if User.query.filter_by(username=username, is_active=True).first():
            flash("❌ Username already taken.")
            return redirect(url_for('users.register'))

        if User.query.filter_by(email=email, is_active=True).first():
            flash("❌ Email already in use.")
            return redirect(url_for('users.register'))

        hashed = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed,
            role=Role(role),
            company_name=company,
            country=country,
            phone=phone
        )

        db.session.add(new_user)
        db.session.commit()

        flash("✅ Registration successful! Please log in.")
        return redirect(url_for('users.login'))

    return render_template('register.html', roles=Role)


# -------------------------------
# Login
# -------------------------------
@users_bp.route('/login', methods=['GET', 'POST'])
def login():


    if current_user.is_authenticated:
        return redirect(url_for('users.profile'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, is_active=True).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("✅ Welcome!")
            return redirect(url_for('users.profile'))
        else:
            flash("❌ Email or Password is incorrect.")
    support_user = User.query.filter_by(username='masoudkh', is_active=True).first()
    return render_template('login.html',support_user=support_user)



# -------------------------------
# Edit Profile
# -------------------------------
@users_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.company_name = request.form['company']
        current_user.country = request.form['country']
        current_user.phone = request.form['phone']
        db.session.commit()
        flash("✅ Profile updated successfully.")
        return redirect(url_for('users.profile'))
    return render_template('edit_profile.html', user=current_user)




# -------------------------------
# Delete account
# -------------------------------
@users_bp.route('/delete', methods=['POST'])
@login_required
def delete_account():
    user_id = current_user.id
    logout_user()
    user = User.query.get(user_id)

    # db.session.delete(user)
    user.is_active = False
    db.session.commit()
    flash("🗑️ Your account has been deleted.")
    return redirect(url_for('users.register'))


# -------------------------------
# Logout
# -------------------------------
@users_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("👋 Successfully logged out.")
    return redirect(url_for('users.login'))


@users_bp.route('/profile')
@login_required
def profile():

    if not current_user.is_active:
        logout_user()
        flash("❌ This account is inactive.")
        return redirect(url_for('users.login'))
    # Continue logic

    # محاسto quantity Ordersی pending (فقط برای Seller)
    pending_orders = 0
    if current_user.role == Role.SELLER :
        from models.order import OrderStatus
        pending_orders = Order.query.filter_by(seller_id=current_user.id, status=OrderStatus.PENDING).count()


    support_user = User.query.filter_by(username='support', is_active=True).first()

    if not support_user:
        # اگر وجود نداشت، First Seller رو بذار
        support_user = User.query.filter_by(role=Role.SELLER, is_active=True).first()


    seller = User.query.filter_by(role=Role.SELLER, is_active=True).first()
    buyer = User.query.filter_by(role=Role.BUYER, is_active=True).first()
    broker = User.query.filter_by(role=Role.BROKER, is_premium=True, is_active=True).first()

    return render_template('users/dashboard.html', user=current_user,support_user=support_user , pending_orders=pending_orders, seller=seller,buyer=buyer, broker=broker)



################################################################


# routes/users/routes.py

from models.order import Order, OrderStatus
#
# @users_bp.route('/order', methods=['GET', 'POST'])
# @login_required
# def place_order():
#     if not current_user.is_authenticated:
#         return redirect(url_for('users.login'))
#
#     if request.method == 'POST':
#         # product = request.form['product']
#         product = request.form.get('product', '').strip()
#         if not product:
#             flash("Select a product.")
#             return redirect(url_for('users.place_order'))
#         # quantity = float(request.form['quantity'])
#         try:
#             quantity = float(request.form.get('quantity', 0))
#             if quantity <= 0:
#                 raise ValueError
#         except ValueError:
#             flash("Invalid quantity.")
#         price = float(request.form['price'])
#         origin_port = request.form['origin_port']
#         destination_port = request.form['destination_port']
#         seller_id = int(request.form['seller_id'])  # receive of Form
#         notes = request.form.get('notes', '')
#
#         # چک کRejectن وجود Seller
#         seller = User.query.get(seller_id)
#         if not seller or seller.role != Role.SELLER:
#             flash("❌ Invalid seller.")
#             return redirect(url_for('users.place_order'))
#
#         # Create order
#         order = Order(
#             product=product,
#             quantity_tons=quantity,
#             price_per_ton=price,
#             origin_port=origin_port,
#             destination_port=destination_port,
#             notes=notes,
#             buyer_id=current_user.id,
#             seller_id=seller.id,
#             status=OrderStatus.PENDING
#         )
#         order.calculate_total()
#
#         db.session.add(order)
#        # db.session.commit()
#
#         # Send Notification to Seller
#         notification = Notification(
#             user_id=seller.id,
#             message=f"Order Newی of {current_user.username} receive کRejectید. (#{order.id})"
#         )
#         db.session.add(notification)
#         #db.session.commit()
#
#         #flash("✅ Order placed successfully.")
#
#         ###33333333333333333333
#         try:
#             db.session.commit()
#             flash("✅ Order and notification registered successfully.")
#         except Exception as e:
#             db.session.rollback()
#             flash("❌ An error occurred.")
#             return redirect(url_for('users.place_order'))
#
#         #3333333333333333333333333
#         return redirect(url_for('users.profile'))
#
#     # Send seller list to template
#     sellers = User.query.filter_by(role=Role.SELLER).all()
#     return render_template('users/place_order.html', sellers=sellers)
#
# # @users_bp.route('/order', methods=['POST'])
# # @login_required
# # def submit_order():
# #     product = request.form['product']
# #     quantity = float(request.form['quantity'])
# #     price = float(request.form['price'])
# #     origin_port = request.form['origin_port']
# #     destination_port = request.form['destination_port']
# #     notes = request.form.get('notes', '')
# #
# #     # Assumption: buyer = current user
# #     buyer_id = current_user.id
# #
# #     # Seller: Currently manual (will be selectable via search in future)
# #     # For testing: First seller in database
# #     seller = User.query.filter_by(role=Role.SELLER).first()
# #     if not seller:
# #         flash("❌ No seller found.")
# #         return redirect(url_for('users.place_order'))
# #
# #     # Broker: If premium user OK, they are the broker
# #     broker_id = current_user.id if current_user.is_premium else None
# #
# #     # Create order
# #     order = Order(
# #         product=product,
# #         quantity_tons=quantity,
# #         price_per_ton=price,
# #         origin_port=origin_port,
# #         destination_port=destination_port,
# #         notes=notes,
# #         buyer_id=buyer_id,
# #         seller_id=seller.id,
# #         broker_id=broker_id,
# #         status=OrderStatus.PENDING
# #     )
# #     order.calculate_total()  # Calculate total price
# #
# #     db.session.add(order)
# #     db.session.commit()
# #
# #     flash(f"✅ Order for {quantity} tons of {product} placed successfully! Order Number: #{order.id}")
# #     return redirect(url_for('users.profile'))
#
#
# @users_bp.route('/orders')
# @login_required
# def my_orders():
#     # All orders where user is buyer, seller, or broker
#     orders = Order.query.filter(
#         (Order.buyer_id == current_user.id) |
#         (Order.seller_id == current_user.id) |
#         (Order.broker_id == current_user.id)
#     ).order_by(Order.created_at.desc()).all()
#     return render_template('users/orders.html', orders=orders)
#
#
#
#
# # Show received orders (Seller)
# @users_bp.route('/seller/orders')
# @login_required
# def seller_orders():
#     # فقط اگر User Seller باشد
#     if current_user.role != Role.SELLER:
#         flash("❌ Access restricted to sellers only")
#         return redirect(url_for('users.profile'))
#
#     # Receive orders where this user is seller and not yet confirmed
#     orders = Order.query.filter_by(seller_id=current_user.id).order_by(Order.created_at.desc()).all()
#
#     return render_template('users/seller_orders.html', orders=orders)
#
#
# # Reject Order
# @users_bp.route('/order/<int:order_id>/reject', methods=['POST'])
# @login_required
# def reject_order(order_id):
#     order = Order.query.get_or_404(order_id)
#
#     if current_user.role != Role.SELLER or order.seller_id != current_user.id:
#         flash("❌ Unauthorized access")
#         return redirect(url_for('users.profile'))
#
#     if order.status == OrderStatus.PENDING:
#         order.status = OrderStatus.CANCELLED
#         db.session.commit()
#         flash(f"🗑️ Order #{order_id} rejected.")
#     else:
#         flash("⚠️ This order status has already been changed.")
#
#     return redirect(url_for('users.seller_orders'))
#
#
# @users_bp.route('/order/<int:order_id>/confirm', methods=['POST'])
# @login_required
# def confirm_order(order_id):
#     order = Order.query.get_or_404(order_id)
#
#     if current_user.role != Role.SELLER or order.seller_id != current_user.id:
#         flash("❌ Unauthorized access")
#         return redirect(url_for('users.profile'))
#
#     if order.status == OrderStatus.PENDING:
#         order.status = OrderStatus.CONFIRMED
#         order.confirmed_at = datetime.now(tehran_tz)
#
#         # 📢 Send Notification to buyer
#         notification = Notification(
#             user_id=order.buyer_id,
#             message=f"Order شما (#{order.id}) تCenter {current_user.company_name or current_user.username} تأیید شد."
#         )
#         db.session.add(notification)
#
#         db.session.commit()
#         flash("✅ Order confirmed and notification sent to buyer.")
#     else:
#         flash("⚠️ این Order agoاً تأیید یا rejectedه است.")
#
#     return redirect(url_for('users.seller_orders'))

# routes/users/order_routes.py
from flask import flash, redirect, url_for, request, render_template
from flask_login import login_required, current_user
from models import db
from models.user import User, Role
from models.order import Order, OrderStatus
from . import users_bp


@users_bp.route('/place_order', methods=['GET', 'POST'])
@login_required
def place_order():
    """
    Place Order با Validation کامل و secure
    """
    if request.method == 'POST':
        try:
            # receive و Validation Loginی
            product = request.form.get('product', '').strip()
            quantity_str = request.form.get('quantity', '').strip()
            price_str = request.form.get('price', '').strip()
            origin_port = request.form.get('origin_port', '').strip()
            destination_port = request.form.get('destination_port', '').strip()
            seller_id_str = request.form.get('seller_id', '').strip()
            notes = request.form.get('notes', '').strip()

            # ✅ Validation فیلدها
            if not product:
                flash("❌ لطفاً Enter product name.")
                return redirect(url_for('users.place_order'))

            if not origin_port or not destination_port:
                flash("❌ لطفاً Select origin and destination.")
                return redirect(url_for('users.place_order'))

            # ✅ Validation کمیت و Price
            try:
                quantity = float(quantity_str)
                price = float(price_str)
                if quantity <= 0 or price <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                flash("❌ Invalid quantity or price.")
                return redirect(url_for('users.place_order'))

            # ✅ Validation Seller
            if not seller_id_str.isdigit():
                flash("❌ Seller Invalid است.")
                return redirect(url_for('users.place_order'))

            seller_id = int(seller_id_str)
            seller = User.query.get(seller_id)

            if not seller:
                flash("❌ Seller comment not found.")
                return redirect(url_for('users.place_order'))

            if seller.role != Role.SELLER:
                flash("❌ Selected user is not a seller.")
                return redirect(url_for('users.place_order'))

            # ✅ تعیین بروکر (فقط اگر Premium User باشد)
            broker_id = current_user.id if current_user.is_premium else None

            # ✅ Create order
            order = Order(
                product=product,
                quantity_tons=quantity,
                price_per_ton=price,
                origin_port=origin_port,
                destination_port=destination_port,
                notes=notes,
                buyer_id=current_user.id,
                seller_id=seller.id,
                broker_id=broker_id,
                status=OrderStatus.PENDING
            )
            order.calculate_total()

            # ✅ Send Notification to Seller
            from models.notification import Notification
            notification = Notification(
                user_id=seller.id,
                message=f"Order Newی of {current_user.username} receive کRejectید. (#{order.id})"
            )

            # ✅ افزودن و ذNoه در یک transaction Unit
            db.session.add(order)
            db.session.add(notification)
            db.session.commit()

            flash("✅ Order placed successfully.")
            return redirect(url_for('users.profile'))

        except Exception as e:
            db.session.rollback()  # ⚠️ openگRejectانی transaction در صورت Error
            print(f"❌ Error در Create order: {e}")
            flash("❌ Error placing order. لطفاً again تلاش کنید.")
            return redirect(url_for('users.place_order'))

    # GET: Show Form — فقط Sellers
    sellers = User.query.filter_by(role=Role.SELLER, is_active=True).all()
    return render_template('users/place_order.html', sellers=sellers)


# -------------------------------
# Show Ordersی User
# -------------------------------
@users_bp.route('/orders')
@login_required
def my_orders():
    orders = Order.query.filter(
        (Order.buyer_id == current_user.id) |
        (Order.seller_id == current_user.id) |
        (Order.broker_id == current_user.id)
    ).order_by(Order.created_at.desc()).all()
    return render_template('users/orders.html', orders=orders)


# -------------------------------
# Show Ordersی Seller
# -------------------------------
@users_bp.route('/seller/orders')
@login_required
def seller_orders():
    if current_user.role != Role.SELLER:
        flash("❌ Only accessible to sellers.")
        return redirect(url_for('users.profile'))

    orders = Order.query.filter_by(seller_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('users/seller_orders.html', orders=orders)


# -------------------------------
# تأیید Order تCenter Seller
# -------------------------------
@users_bp.route('/order/<int:order_id>/confirm', methods=['POST'])
@login_required
def confirm_order(order_id):
    order = Order.query.get_or_404(order_id)

    if current_user.role != Role.SELLER or order.seller_id != current_user.id:
        flash("❌ Unauthorized access.")
        return redirect(url_for('users.profile'))

    if order.status == OrderStatus.PENDING:
        order.status = OrderStatus.CONFIRMED
        order.confirmed_at = datetime.now(tehran_tz)

        # Send Notification to buyer
        from models.notification import Notification
        notification = Notification(
            user_id=order.buyer_id,
            message=f"Order شما (#{order.id}) تCenter {current_user.username} تأیید شد."
        )
        db.session.add(notification)
        db.session.commit()

        flash("✅ Order تأیید شد و Notification Send گRejectید.")
    else:
        flash("⚠️ این Order agoاً تأیید یا rejectedه است.")

    return redirect(url_for('users.seller_orders'))


# -------------------------------
# Reject Order تCenter Seller
# -------------------------------
@users_bp.route('/order/<int:order_id>/reject', methods=['POST'])
@login_required
def reject_order(order_id):
    order = Order.query.get_or_404(order_id)

    if current_user.role != Role.SELLER or order.seller_id != current_user.id:
        flash("❌ Unauthorized access.")
        return redirect(url_for('users.profile'))

    if order.status == OrderStatus.PENDING:
        order.status = OrderStatus.CANCELLED
        db.session.commit()
        flash(f"🗑️ Order #{order_id} rejected.")
    else:
        flash("⚠️ This order status has already been changed.")

    return redirect(url_for('users.seller_orders'))


@users_bp.route('/notifications')
@login_required
def notifications():
    # خواندن All Notifications
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()

    # علامت‌گذاری to Title Read
    for n in notifs:
        if not n.is_read:
            n.is_read = True
    db.session.commit()

    return render_template('users/notifications.html', notifications=notifs)


@users_bp.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    # ✅ فقط Users premium می‌تونن Chat کنن
    if not current_user.is_premium:
        flash("❌ Access restricted: Only premium users can chat.", "error")
        return redirect(url_for('users.profile'))

    # لیست Users (فقط premium‌ها)
    users = User.query.filter(
        User.id != current_user.id,
        User.is_premium == True
    ).all()

    receiver_id = request.args.get('receiver_id', type=int)
    receiver = User.query.get(receiver_id) if receiver_id else None

    # ✅ اگر گیرنده وجود نداشته ok یا premium نok
    if receiver and not receiver.is_premium:
        flash("❌ این Premium User نیست و نمی‌توانید با او Chat کنید.", "error")
        receiver = None

    # Send Message
    if request.method == 'POST' and receiver:
        content = request.form['content'].strip()
        if content:
            # ایجاد Message
            msg = Message(
                sender_id=current_user.id,
                receiver_id=receiver.id,
                content=content
            )
            db.session.add(msg)
            db.session.commit()

            # ✅ Send Notification to گیرنده
            notification = Notification(
                user_id=receiver.id,
                message=f"📩 Message Newی of {current_user.username} receive کRejectید."
            )
            db.session.add(notification)
            db.session.commit()

            flash("✉️ Message Send شد.")
        return redirect(url_for('users.chat', receiver_id=receiver.id))

    # receive Messages
    messages = []
    if receiver:
        messages = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == receiver.id)) |
            ((Message.sender_id == receiver.id) & (Message.receiver_id == current_user.id))
        ).order_by(Message.created_at.asc()).all()

        # علامت‌گذاری Messagesی receiveی to Title Read
        for m in messages:
            if m.receiver_id == current_user.id and not m.is_read:
                m.is_read = True
        db.session.commit()

    return render_template('users/chat.html', users=users, receiver=receiver, messages=messages)







from flask import g

@users_bp.app_context_processor
def inject_support_user():
    if current_user.is_authenticated:
        # مثلاً Seller first یا User با username='support'
        support_user = User.query.filter_by(username='support', is_active=True).first()
        if not support_user:
            support_user = User.query.filter_by(role=Role.SELLER, is_active=True).first()
        return {'support_user': support_user}
    return {'support_user': None}


####################################
import requests
from flask import request
import json
from models import DataProvider
from functools import wraps

provider = DataProvider()
country_codes = provider.COUNTRY_CODES

#
# def get_imo(self):
#     imo=9679593
#     return imo
#
#
# @users_bp.route('/vessel_finder', methods=['GET', 'POST'])
# @login_required
# def vessel_finder():
#     # Receive coordinates from URL parameters
#     imo = get_imo(int)
#     url = f"https://api.searoutes.com/vessel/v2/{imo}/position"
#     headers = {
#         "X-API-Key": 'zXlhor8hMV9fXyeZ3nero4aPpYAw39eU37KYP9ne',#"Ink2LLxsDW7H0iEY9KnRpaR9p9RsxMSm5dDnF9kP",
#         "Content-Type": "application/json"
#     }
#
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
#     a=response.json()
#     coordinates = a[0]['position']['geometry']['coordinates']
#     name = a[0]['info']['name']
#     imo = a[0]['info']['imo']
#     mmsi = a[0]['info']['mmsi']
#     speed = a[0]['position']['properties']['speed']
#     destination = a[0]['position']['properties']['destination']
#     date_arrival = a[0]['position']['properties']['eta']
#     long = coordinates[0]
#     lat  =coordinates[1]
#
#     latitude = request.args.get('latitude', None)
#     longitude = request.args.get('longitude', None)
#
#     # If coordinates exist, send to map page
#     return render_template('users/map_vessel_finder.html', latitude=lat, longitude=long,imo=imo,mmsi=mmsi,name=name,destination=destination,speed=speed,date_arrival=date_arrival)
#

@users_bp.route('/vessel_finder', methods=['GET', 'POST'])
@login_required
def vessel_finder():
    if not current_user.is_premium:
        flash("❌ دسترسی فقط برای Users premium مجof است.", "error")
        return redirect(url_for('users.profile'))

    # فقط در صورت POST و receive IMO
    if request.method == 'POST':
        imo = request.form.get('imo', '').strip()

        # Validation
        if not imo or not imo.isdigit() or len(imo) != 7:
            flash("❌ Please enter a valid 7-digit IMO number.", "error")
            return render_template('users/vessel_finder.html')

        url = f"https://api.searoutes.com/vessel/v2/{imo}/position"
        headers = {
            "X-API-Key": "zXlhor8hMV9fXyeZ3nero4aPpYAw39eU37KYP9ne",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                flash("❌ No data found for this ship.", "error")
                return render_template('users/vessel_finder.html')

            pos = data[0]['position']
            info = data[0]['info']

            return render_template(
                'users/vessel_finder.html',
                latitude=pos['geometry']['coordinates'][1],
                longitude=pos['geometry']['coordinates'][0],
                imo=info['imo'],
                mmsi=info['mmsi'],
                name=info['name'],
                destination=pos['properties'].get('destination', 'Unknown'),
                speed=pos['properties'].get('speed', 'Unknown'),
                date_arrival=pos['properties'].get('eta', 'Unknown')
            )

        except requests.exceptions.Timeout:
            flash("❌ Request timed out. لطفاً again تلاش کنید.", "error")
        except requests.exceptions.RequestException as e:
            flash("❌ Error connecting to ship tracking service.", "error")
        except (KeyError, IndexError) as e:
            flash("❌ داده‌های receiveی Invalid هسTonد.", "error")

    # GET یا Error: Show Form
    return render_template('users/vessel_finder.html')
######################################TEST

# Show Roleه
@users_bp.route('/map')
@login_required
def show_map():
    if not current_user.is_premium:
        flash("❌ Only premium users can access this role.")
        return redirect(url_for('users.profile'))
    ports = Port.query.all()
    ports_data = [port.to_dict() for port in ports]
    ports_data = [
        {
            "name": port.name,
            "country": port.country,
            "location": [port.latitude, port.longitude]
        } for port in ports
    ]
    #ports = Port.query.all()
    return render_template('users/map.html', ports=ports_data )


##############################################################test2

# routes/users/routes.py
from flask import jsonify


@users_bp.route('/api/ports', methods=['GET'])
@login_required
def get_ports():
    # فقط Users premium می‌تونن ببینن
    if not current_user.is_premium:
        return jsonify({'error': 'Access denied: فقط Users premium'}), 403

    # receive All پورت‌ها
    ports = Port.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'country': p.country,
        'location': [p.latitude, p.longitude]
    } for p in ports])


@users_bp.route('/add_port', methods=['POST'])
@login_required
def add_port():
    if current_user.role != Role.SELLER:
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    port = Port(
        name=data['name'],
        country=data['country'],
        latitude=data['latitude'],
        longitude=data['longitude']
    )
    db.session.add(port)
    db.session.commit()
    return jsonify({'message': 'Port added.', 'port': port.to_dict()})


@users_bp.route('/update_port/<port_id>', methods=['PUT'])
@login_required
def update_port(port_id):
    if current_user.role != Role.SELLER:
        return jsonify({'error': 'Access denied'}), 403

    # ✅ چک کRejectن اینکه port_id عددی ok
    if not port_id.isdigit():
        return jsonify({'error': 'Port ID must be a positive number.'}), 400

    port_id = int(port_id)

    port = Port.query.get_or_404(port_id)
    data = request.get_json()

    port.name = data['name']
    port.country = data['country']
    port.latitude = data['latitude']
    port.longitude = data['longitude']

    db.session.commit()
    return jsonify({'message': 'پورت successfully Update شد.'})


@users_bp.route('/delete_port/<port_id>', methods=['DELETE'])
@login_required
def delete_port(port_id):
    if current_user.role != Role.SELLER:
        return jsonify({'error': 'Access denied'}), 403
    if not port_id.isdigit():
        return jsonify({'error': 'Port ID must be a positive number.'}), 400

    port_id = int(port_id)
    port = Port.query.get_or_404(port_id)
    db.session.delete(port)
    db.session.commit()
    return jsonify({'message': 'پورت deleted.'})

# @users_bp.route('/test')
# def test():
#     return "✅ route /users/test کار می‌کنه!"

####################################################################

import os
from flask import request, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.premium_request import PremiumRequest

# Main upgrade route
@users_bp.route('/upgrade_to_premium')
@login_required
def upgrade_to_premium():
    # Latest request from User
    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()
    # receive finish request‌ها برای Show Dateچه
    requests = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(
        PremiumRequest.submitted_at.desc()).all()

    if req:
        if req.status == 'approved':
            flash("✅ You are already a premium user.")
            return redirect(url_for('users.profile'))
        elif req.status == 'pending':
            flash("⚠️ Your request is under review.")
            return redirect(url_for('users.payment_confirmation'))

    # Send `req` to themeپلیت
    return render_template('users/upgrade_premium.html', req=req, requests=requests)

# Start process (ایجاد request New)
@users_bp.route('/start_upgrade', methods=['POST'])
@login_required
def start_upgrade():
    # همیشه یک request New ایجاد می‌کنیم
    req = PremiumRequest(user_id=current_user.id)
    db.session.add(req)
    db.session.commit()

    flash("Upgrade process started. لطفاً mobile number خود را تأیید کنید.")
    return redirect(url_for('users.verify_phone'))

# # Upload documents
@users_bp.route('/upload_documents', methods=['GET', 'POST'])
@login_required
def upload_documents():
    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()



    if not req or not req.email_verified:
        return redirect(url_for('users.verify_email'))

    if req.docs_verified:
        return redirect(url_for('users.make_payment'))

    # if not req:
    #     return redirect(url_for('users.upgrade_to_premium'))

    upload_folder = 'static/uploads/documents/'
    os.makedirs(upload_folder, exist_ok=True)

    if request.method == 'POST':
        if 'passport' in request.files:
            file = request.files['passport']
            if file.filename != '':
                filename = secure_filename(f"passport_{current_user.id}_{file.filename}")
                file.save(os.path.join(upload_folder, filename))
                req.passport_file = filename

        if 'license' in request.files:
            file = request.files['license']
            if file.filename != '':
                filename = secure_filename(f"license_{current_user.id}_{file.filename}")
                file.save(os.path.join(upload_folder, filename))
                req.license_file = filename

        req.docs_verified = True
        db.session.commit()
        flash("Documents uploaded successfully.")
        return redirect(url_for('users.make_payment'))

    return render_template('users/upload_documents.html', req=req)

# پRejectاخت و upload receipt
@users_bp.route('/make_payment', methods=['GET', 'POST'])
@login_required
def make_payment():
    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()


    if not req or not req.docs_verified:
        return redirect(url_for('users.upload_documents'))

    if req.payment_verified:
        return redirect(url_for('users.payment_confirmation'))


    if request.method == 'POST':
        if 'receipt' in request.files:
            file = request.files['receipt']
            if file.filename != '':
                filename = secure_filename(f"receipt_{current_user.id}_{file.filename}")
                file.save(os.path.join('static/uploads/', filename))
                req.payment_receipt = filename

                req.status = 'pending'
                req.payment_verified = True
                db.session.commit()
                flash("receipt پRejectاخت receive شد. Under review...")
                # Send Notification to Admin
                notify_admin_of_new_request(req)
                return redirect(url_for('users.payment_confirmation'))

    return render_template('users/make_payment.html', req=req)

# Final approval
@users_bp.route('/payment_confirmation')
@login_required
def payment_confirmation():
    return render_template('users/payment_confirmation.html')

# --- تابع کمکی: Notification to Admin ---
def notify_admin_of_new_request(req):
    from flask_mail import Message
    from app import mail  # فرض می‌کنیم mail Tonظیم شده

    admins = User.query.filter_by(role='admin', is_active=True).all()
    emails = [a.email for a in admins if a.email]

    if emails:
        msg = Message(
            subject="🔔 request New upgrade to Premium User",
            recipients=emails,
            body=f"User {req.user.username} یک request New Send کRejectه است."
        )
        mail.send(msg)
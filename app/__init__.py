from dotenv import load_dotenv
load_dotenv()

import os
import json
import requests
import base64
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from .forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from .db_models import db, User, Item
from itsdangerous import URLSafeTimedSerializer
from .funcs import mail, fulfill_order
from .admin.routes import admin
from sqlalchemy import func

app = Flask(__name__)
app.register_blueprint(admin)

app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DB_URI"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_USERNAME'] = os.environ["EMAIL"]
app.config['MAIL_PASSWORD'] = os.environ["PASSWORD"]
app.config['MAIL_SERVER'] = "smtp.googlemail.com"
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_PORT'] = 587

Bootstrap(app)
db.init_app(app)
mail.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

with app.app_context():
    db.create_all()

CATEGORY_LABELS = {
    'Apple': 'Smartphones',
    'laptop': 'Laptops',
    'Television': 'TV & Home Entertainment'
}

@app.context_processor
def inject_now():
    """ sends datetime to templates as 'now' """
    return {'now': datetime.utcnow()}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.template_filter('currency_kes')
def currency_kes(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value
    return f"KES {value:.0f}"

def build_category_data():
    distinct = Item.query.with_entities(Item.category).distinct().all()
    categories = []
    for cat, in distinct:
        if not cat:
            continue
        categories.append({
            'value': cat,
            'label': CATEGORY_LABELS.get(cat, cat.title())
        })
    categories.sort(key=lambda c: c['label'])
    return categories

def build_home_context(items, search=False, query=None, selected_category='All', show_catalog=False):
    categories = build_category_data()
    hero_item = Item.query.filter(Item.category == 'Apple').order_by(Item.id.desc()).first()
    if not hero_item:
        hero_item = Item.query.order_by(Item.id.desc()).first()
    featured_products = Item.query.order_by(Item.price.desc()).limit(3).all()
    selected_label = 'All products' if selected_category == 'All' else CATEGORY_LABELS.get(selected_category, selected_category.title())
    return dict(
        items=items,
        hero_item=hero_item,
        categories=categories,
        selected_category=selected_category,
        selected_category_label=selected_label,
        featured_products=featured_products,
        category_labels=CATEGORY_LABELS,
        search=search,
        query=query,
        show_catalog=show_catalog
    )

def get_product_content(item):
    name = (item.name or '').lower()
    specs = [
        ("Warranty", "12 months manufacturer warranty"),
        ("Delivery", "Same-day delivery within Nairobi"),
        ("Payments", "M-Pesa STK push, Visa, Mastercard")
    ]

    if "iphone 12 mini" in name:
        specs = [
            ("Display", "5.4\" Super Retina XDR OLED"),
            ("Storage", "128GB"),
            ("Camera", "12MP dual rear camera, 12MP TrueDepth front camera"),
            ("Chip", "A14 Bionic chip"),
            ("Connectivity", "5G, Dual SIM (nano + eSIM)")
        ] + specs
    elif "iphone 12" in name:
        specs = [
            ("Display", "6.1\" Super Retina XDR OLED"),
            ("Storage", "128GB"),
            ("Camera", "12MP dual rear camera with Night mode"),
            ("Chip", "A14 Bionic chip"),
            ("Battery", "MagSafe fast charging support")
        ] + specs
    elif "iphone 11" in name:
        specs = [
            ("Display", "6.1\" Liquid Retina HD"),
            ("Storage", "128GB"),
            ("Camera", "12MP dual Ultra Wide and Wide cameras"),
            ("Chip", "A13 Bionic chip"),
            ("Water resistance", "IP68 up to 2 metres for 30 minutes")
        ] + specs
    elif "nitro" in name:
        specs = [
            ("Processor", "Intel Core i7 11th Gen"),
            ("Graphics", "NVIDIA GeForce RTX 3060 6GB"),
            ("Memory", "16GB DDR4 RAM"),
            ("Storage", "512GB NVMe SSD"),
            ("Display", "15.6\" FHD 144Hz IPS"),
        ] + specs
    elif "macbook" in name:
        specs = [
            ("Chip", "Apple M1 Pro (10-core CPU, 16-core GPU)"),
            ("Memory", "16GB unified memory"),
            ("Storage", "512GB SSD storage"),
            ("Display", "14\" Liquid Retina XDR"),
            ("Battery life", "Up to 17 hours Apple TV app movie playback")
        ] + specs
    elif "mi tv" in name:
        specs = [
            ("Screen size", "55\" UHD 4K HDR"),
            ("Smart TV", "Android TV with Google Assistant"),
            ("Audio", "20W Dolby + DTS-HD"),
            ("Connectivity", "Wi-Fi, Bluetooth 5.0, 3x HDMI, 2x USB"),
            ("Extras", "Chromecast built-in, PatchWall OS")
        ] + specs
    else:
        specs = [
            ("Key highlight", item.details or "Premium electronics from Ebenezer"),
        ] + specs

    reviews = [
        {"name": "Wanjiru K.", "rating": 5, "time": "2 days ago", "comment": "Authentic product, sealed box and the M-Pesa checkout was seamless."},
        {"name": "Brian O.", "rating": 4, "time": "1 week ago", "comment": "Delivered same day in Nairobi CBD. Helpful support team with setup."},
        {"name": "Naomi N.", "rating": 5, "time": "3 weeks ago", "comment": "Best price I found locally. Highly recommend Ebenezer Electronics."}
    ]

    faqs = [
        {"question": "Do you deliver outside Nairobi?", "answer": "Yes, we ship countrywide within 24-48 hours via G4S or Fargo. Delivery fees depend on location."},
        {"question": "Can I pay on delivery?", "answer": "For Nairobi we support pay-on-delivery via M-Pesa. Upcountry orders require a 30% deposit."},
        {"question": "Is the warranty valid in Kenya?", "answer": "Absolutely. All devices come with official manufacturer warranty honoured locally."}
    ]

    return specs, reviews, faqs

@app.route("/")
def home():
    selected_category = request.args.get('category', 'All')
    items_query = Item.query.order_by(Item.id.desc())
    if selected_category and selected_category.lower() != 'all':
        items_query = items_query.filter(func.lower(Item.category) == selected_category.lower())
    items = items_query.all()
    show_catalog = bool(selected_category and selected_category.lower() != 'all')
    context = build_home_context(
        items,
        selected_category=selected_category if selected_category else 'All',
        show_catalog=show_catalog
    )
    return render_template("home.html", **context)


@app.route("/products")
def products():
    items = Item.query.order_by(Item.id.desc()).all()
    context = build_home_context(items, selected_category='All', show_catalog=True)
    return render_template("home.html", **context)

@app.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user == None:
            flash(f'User with email {email} doesn\'t exist!<br> <a href={url_for("register")}>Register now!</a>', 'error')
            return redirect(url_for('login'))
        elif check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Email and password incorrect!!", "error")
            return redirect(url_for('login'))
    return render_template("login.html", form=form)

@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash(f"User with email {user.email} already exists!!<br> <a href={url_for('login')}>Login now!</a>", "error")
            return redirect(url_for('register'))
        new_user = User(name=form.name.data,
                        email=form.email.data,
                        password=generate_password_hash(
                                    form.password.data,
                                    method='pbkdf2:sha256',
                                    salt_length=8),
                        phone=form.phone.data)
        db.session.add(new_user)
        db.session.commit()
        # send_confirmation_email(new_user.email)
        flash('Thanks for registering! You may login now.', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/add/<id>", methods=['POST'])
def add_to_cart(id):
    if not current_user.is_authenticated:
        flash(f'You must login first!<br> <a href={url_for("login")}>Login now!</a>', 'error')
        return redirect(url_for('login'))

    item = Item.query.get(id)
    if request.method == "POST":
        quantity = request.form["quantity"]
        current_user.add_to_cart(id, quantity)
        flash(f'''{item.name} successfully added to the <a href=cart>cart</a>.<br> <a href={url_for("cart")}>view cart!</a>''','success')
        return redirect(url_for('home'))

@app.route("/cart")
@login_required
def cart():
    price = 0
    items = []
    quantity = []
    for cart in current_user.cart:
        items.append(cart.item)
        quantity.append(cart.quantity)
        price += cart.item.price*cart.quantity
    return render_template('cart.html', items=items, price=price, quantity=quantity, category_labels=CATEGORY_LABELS)

@app.route('/orders')
@login_required
def orders():
    return render_template('orders.html', orders=current_user.orders)

@app.route("/remove/<id>/<quantity>")
@login_required
def remove(id, quantity):
    current_user.remove_from_cart(id, quantity)
    return redirect(url_for('cart'))

@app.route('/item/<int:id>')
def item(id):
    item = Item.query.get(id)
    if not item:
        abort(404)
    specs, reviews, faqs = get_product_content(item)
    category_label = CATEGORY_LABELS.get(item.category, item.category.title())
    return render_template('item.html', item=item, specs=specs, reviews=reviews, faqs=faqs, category_label=category_label)

@app.route('/search')
def search():
    query = request.args['query']
    search = "%{}%".format(query)
    items = Item.query.filter(Item.name.like(search)).all()
    context = build_home_context(items, search=True, query=query, show_catalog=True)
    return render_template('home.html', **context)

@app.route('/payment_success')
def payment_success():
    return render_template('success.html')

@app.route('/payment_failure')
def payment_failure():
    return render_template('failure.html')

# --- M-Pesa Integration ---
def get_mpesa_access_token():
    consumer_key = os.environ['MPESA_CONSUMER_KEY']
    consumer_secret = os.environ['MPESA_CONSUMER_SECRET']
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(api_URL, auth=(consumer_key, consumer_secret))
    print("M-Pesa token response:", r.status_code, r.text)  # Debug print
    if r.status_code != 200:
        raise Exception(f"Failed to get token: {r.status_code} {r.text}")
    return r.json()['access_token']

def generate_password():
    shortcode = os.environ['MPESA_SHORTCODE']
    passkey = os.environ['MPESA_PASSKEY']
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = shortcode + passkey + timestamp
    encoded = base64.b64encode(data_to_encode.encode())
    return encoded.decode('utf-8'), timestamp

@app.route('/mpesa_checkout', methods=['POST'])
@login_required
def mpesa_checkout():
    phone = request.form['phone']
    try:
        # Convert the amount to a float, then to an integer (M-Pesa expects whole numbers)
        amount = int(float(request.form['amount']))
    except (ValueError, TypeError):
        flash("Invalid amount.", "error")
        return redirect(url_for('cart'))

    if amount < 1:
        flash("Amount must be at least 1.", "error")
        return redirect(url_for('cart'))

    access_token = get_mpesa_access_token()
    password, timestamp = generate_password()
    headers = {"Authorization": f"Bearer {access_token}"}
    # Attach user id to callback URL so we can fulfill the order on callback
    base_callback="https://semiexpositive-amiee-refractorily.ngrok-free.dev/mpesa_callback"
    
    callback_with_uid = f"{base_callback}?uid={current_user.id}"
    payload = {
        "BusinessShortCode": 174379,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": 174379,
        "PhoneNumber": phone,
        "CallBackURL": callback_with_uid,
        "AccountReference": str(current_user.id),
        "TransactionDesc": "Cart Payment"
    }
    print(payload)    
    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        headers=headers,
        json=payload
    )
    res = response.json()
    if res.get("ResponseCode") == "0":
        flash("M-Pesa payment initiated. Check your phone to complete the payment.", "success")
        return redirect(url_for('orders'))
    else:
        error_msg = res.get("errorMessage", res.get("errorCode", "Unknown error"))
        flash(f"M-Pesa payment failed: {error_msg}", "error")
        return redirect(url_for('cart'))

def send_payment_sms_to_business(amount, receipt, customer_phone):
    """Send SMS to business owner when M-Pesa payment is received.
    Uses Africa's Talking API. Set BUSINESS_PHONE, AFRICAS_TALKING_API_KEY,
    and AFRICAS_TALKING_USERNAME in .env to enable.
    """
    business_phone = os.environ.get('BUSINESS_PHONE')
    api_key = os.environ.get('AFRICAS_TALKING_API_KEY')
    username = os.environ.get('AFRICAS_TALKING_USERNAME', 'sandbox')
    if not all([business_phone, api_key]):
        return
    msg = f"Ebenezer Electronics: You received KES {amount}. Receipt: {receipt or 'N/A'}. From: {customer_phone or 'N/A'}"
    try:
        resp = requests.post(
            'https://api.africastalking.com/version1/messaging',
            headers={'Content-Type': 'application/x-www-form-urlencoded', 'apikey': api_key},
            data={
                'username': username,
                'to': business_phone,
                'message': msg,
            },
            timeout=10,
        )
        if resp.status_code != 201:
            print("SMS send failed:", resp.status_code, resp.text)
    except Exception as e:
        print("SMS send error:", e)


@app.route('/mpesa_callback', methods=['POST'])
def mpesa_callback():
    """Safaricom Daraja STK push callback endpoint.
    Creates an order on successful payment.
    Sends SMS to business owner when payment is received.
    """
    try:
        data = request.get_json(silent=True, force=True) or {}
        stk_callback = (data.get('Body') or {}).get('stkCallback') or {}
        result_code = stk_callback.get('ResultCode')
        # Extract optional metadata
        callback_metadata = stk_callback.get('CallbackMetadata') or {}
        items = callback_metadata.get('Item') or []
        amount = None
        phone_number = None
        receipt = None
        for item in items:
            if item.get('Name') == 'Amount':
                amount = item.get('Value')
            elif item.get('Name') == 'PhoneNumber':
                phone_number = item.get('Value')
            elif item.get('Name') == 'MpesaReceiptNumber':
                receipt = item.get('Value')
        # Determine the user id: prefer uid passed in callback URL, else AccountReference if provided
        uid = request.args.get('uid')
        if not uid:
            uid = stk_callback.get('AccountReference')
        if result_code == 0 and uid:
            try:
                session_like = {'client_reference_id': int(uid)}
                fulfill_order(session_like)
                # Notify business owner of payment received
                send_payment_sms_to_business(amount or '—', receipt or '—', str(phone_number) if phone_number else '—')
            except Exception as fulfillment_error:
                # Log and still acknowledge to Safaricom to avoid retries
                print("Fulfillment error:", fulfillment_error)
        # Always acknowledge callback
        return {"ResultCode": 0, "ResultDesc": "Accepted"}, 200
    except Exception as e:
        print("Callback error:", e)
        # Acknowledge with success to prevent repeated retries, but log for investigation
        return {"ResultCode": 0, "ResultDesc": "Accepted"}, 200
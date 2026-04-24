import os
from functools import lru_cache

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
PREFERRED_IMAGE_MARKERS = ("-real3", "-real2", "-real", "_real3", "_real2", "_real")
GENERATED_FALLBACKS = {
    "tv": "/static/uploads/generated/tv_pro.png",
    "laptop": "/static/uploads/generated/laptop_pro.png",
    "phone": "/static/uploads/generated/phone_pro.png",
    "watch": "/static/uploads/generated/watch_pro.png",
    "console": "/static/uploads/generated/console_pro.png",
    "headphones": "/static/uploads/generated/headphones_pro.png",
}


@lru_cache(maxsize=512)
def resolve_professional_image(image_url):
    """Prefer polished local image variants when they exist."""
    if not image_url or not image_url.startswith("/static/uploads/"):
        return image_url

    filename = image_url.replace("/static/uploads/", "", 1)
    if "/" in filename:
        return image_url

    stem, extension = os.path.splitext(filename)
    extension = extension.lower()
    if extension not in IMAGE_EXTENSIONS:
        return image_url

    preferred_variants = []
    for marker in PREFERRED_IMAGE_MARKERS:
        for ext in IMAGE_EXTENSIONS:
            preferred_variants.append(f"{stem}{marker}{ext}")

    for candidate in preferred_variants:
        candidate_path = os.path.join(UPLOADS_DIR, candidate)
        if os.path.exists(candidate_path):
            return f"/static/uploads/{candidate}"

    try:
        sibling_files = [
            sibling for sibling in os.listdir(UPLOADS_DIR)
            if sibling.startswith(stem)
        ]
    except FileNotFoundError:
        return image_url

    ranked_candidates = []
    for sibling in sibling_files:
        sibling_stem, sibling_ext = os.path.splitext(sibling)
        sibling_ext = sibling_ext.lower()
        sibling_name = sibling.lower()

        if sibling == filename or sibling_ext not in IMAGE_EXTENSIONS:
            continue
        if "placeholder" in sibling_name:
            continue
        if not any(marker in sibling_name for marker in ("real", "pro", "generated")):
            continue

        score = 0
        if "real3" in sibling_name:
            score += 40
        elif "real2" in sibling_name:
            score += 30
        elif "real" in sibling_name:
            score += 20
        if "pro" in sibling_name:
            score += 10
        if sibling_ext == ".png":
            score += 3
        elif sibling_ext == ".webp":
            score += 2
        elif sibling_ext == ".jpg":
            score += 1
        ranked_candidates.append((score, sibling))

    if ranked_candidates:
        ranked_candidates.sort(reverse=True)
        return f"/static/uploads/{ranked_candidates[0][1]}"

    return image_url


def get_generated_fallback(item_name, category, image_url):
    """Choose the closest existing generic pro image when a product has no good match."""
    haystack = f"{item_name or ''} {category or ''} {image_url or ''}".lower()

    if any(keyword in haystack for keyword in ("laptop", "macbook", "notebook", "thinkpad", "ideapad", "spectre", "pavilion", "swift", "xps", "zenbook", "nitro")):
        return GENERATED_FALLBACKS["laptop"]
    if any(keyword in haystack for keyword in ("tv", "oled", "qled", "bravia", "uhd", "hdr", "nanocell", "uled")):
        return GENERATED_FALLBACKS["tv"]
    if any(keyword in haystack for keyword in ("phone", "galaxy", "iphone", "redmi", "infinix", "oppo", "tecno", "xiaomi")):
        return GENERATED_FALLBACKS["phone"]
    if any(keyword in haystack for keyword in ("watch", "wearable")):
        return GENERATED_FALLBACKS["watch"]
    if any(keyword in haystack for keyword in ("playstation", "xbox", "console", "gaming")):
        return GENERATED_FALLBACKS["console"]
    if any(keyword in haystack for keyword in ("headphone", "earbud", "speaker", "sony wh", "jbl")):
        return GENERATED_FALLBACKS["headphones"]
    return image_url


# =========================
# USER MODEL
# =========================

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(250), nullable=False)

    admin = db.Column(db.Boolean, default=False)
    email_confirmed = db.Column(db.Boolean, default=False)

    cart = db.relationship('Cart', backref='buyer', lazy=True)
    orders = db.relationship("Order", backref='customer', lazy=True)

    def get_reset_token(self):
        from itsdangerous import URLSafeTimedSerializer
        from flask import current_app
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
        from flask import current_app
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except (SignatureExpired, BadSignature):
            return None
        return User.query.get(user_id)


    def add_to_cart(self, itemid, quantity):
        item_to_add = Cart(
            itemid=itemid,
            uid=self.id,
            quantity=quantity
        )

        db.session.add(item_to_add)
        db.session.commit()


    def remove_from_cart(self, itemid, quantity):
        item_to_remove = Cart.query.filter_by(
            itemid=itemid,
            uid=self.id,
            quantity=quantity
        ).first()

        if item_to_remove:
            db.session.delete(item_to_remove)
            db.session.commit()


# =========================
# ITEM MODEL
# =========================

class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(250), nullable=False)
    details = db.Column(db.String(250), nullable=False)

    price_id = db.Column(db.String(250))

    stock = db.Column(db.Integer, nullable=False, default=0)

    
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    orders = db.relationship("Ordered_item", backref="item", lazy=True)
    in_cart = db.relationship("Cart", backref="item", lazy=True)

    @property
    def display_image(self):
        resolved_image = resolve_professional_image(self.image)
        if "/static/uploads/generated/" in resolved_image:
            return get_generated_fallback(self.name, self.category, resolved_image)
        return resolved_image

# =========================
# CART MODEL
# =========================

class Cart(db.Model):
    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)

    uid = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    itemid = db.Column(
        db.Integer,
        db.ForeignKey('items.id'),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )


# =========================
# ORDER MODEL
# =========================

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    uid = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    date = db.Column(db.DateTime, nullable=False)

    status = db.Column(db.String(50), nullable=False)

    total_amount = db.Column(db.Float, nullable=False, default=0)  

    items = db.relationship(
        "Ordered_item",
        backref="order",
        lazy=True,
        cascade="all, delete"
    )


# =========================
# ORDERED ITEM MODEL
# =========================

class Ordered_item(db.Model):
    __tablename__ = "ordered_items"

    id = db.Column(db.Integer, primary_key=True)

    oid = db.Column(
        db.Integer,
        db.ForeignKey('orders.id'),
        nullable=False
    )

    itemid = db.Column(
        db.Integer,
        db.ForeignKey('items.id'),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

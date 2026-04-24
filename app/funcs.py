import os, datetime
from flask import render_template, url_for, redirect
from itsdangerous import URLSafeTimedSerializer
from flask_login import current_user
from flask_mail import Mail, Message
from dotenv import load_dotenv
from .db_models import Order, Ordered_item, db, User


load_dotenv()
mail = Mail()



def fulfill_order(session):
    """Fulfils order on successful payment"""

    uid = session['client_reference_id']

    order = Order(
        uid=uid,
        date=datetime.datetime.now(),
        status="Paid"
    )

    db.session.add(order)
    db.session.commit()

    current_user = User.query.get(uid)

    for cart in current_user.cart:

        ordered_item = Ordered_item(
            oid=order.id,
            itemid=cart.item.id,
            quantity=cart.quantity,
            price=cart.item.price   # ⭐ VERY IMPORTANT
        )

        db.session.add(ordered_item)

        current_user.remove_from_cart(
            cart.item.id,
            cart.quantity
        )

    db.session.commit()

def admin_only(func):
	"""Decorator for giving access to authorized users only."""
	def wrapper(*args, **kwargs):
		# redirect unauthenticated or non-admin users to the admin login page
		if current_user.is_authenticated and current_user.admin == 1:
			return func(*args, **kwargs)
		return redirect(url_for('admin.login'))
	wrapper.__name__ = func.__name__
	return wrapper
		
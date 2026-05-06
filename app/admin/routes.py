from flask import render_template, url_for, flash, redirect
from sqlalchemy import func

from ..db_models import Order, Item, User, Ordered_item, db
from ..admin.forms import AddItemForm
from ..funcs import admin_only
from . import admin





@admin.route("/")
@admin_only
def admin_home():
    return redirect(url_for("admin.dashboard"))



@admin.route("/dashboard")
@admin_only
def dashboard():

    total_revenue = (
        db.session.query(db.func.sum(Ordered_item.price * Ordered_item.quantity))
        .join(Order)
        .filter(Order.status == "Paid")
        .scalar()
        or 0
    )

    total_products = Item.query.count()

    total_customers = User.query.count()

    total_orders = Order.query.count()

    return render_template(
        "admin/dashboard.html",
        total_revenue=total_revenue,
        total_products=total_products,
        total_customers=total_customers,
        total_orders=total_orders,
    )





@admin.route("/reports/sales")
@admin_only
def sales_report():

    orders = Order.query.order_by(Order.date.desc()).all()

    total_revenue = (
        db.session.query(func.sum(Order.total_amount))
        .filter(Order.status == "Paid")
        .scalar()
        or 0
    )

    return render_template(
        "admin/sales_report.html", orders=orders, total_revenue=total_revenue
    )




@admin.route("/reports/inventory")
@admin_only
def inventory_report():

    products = Item.query.order_by(Item.id.desc()).all()

    return render_template("admin/inventory_report.html", products=products)




@admin.route("/reports/customers")
@admin_only
def customer_report():

    customers = User.query.all()

    customer_data = []

    for customer in customers:
        total_orders = Order.query.filter_by(uid=customer.id).count()

        total_spent = (
            db.session.query(func.sum(Order.total_amount))
            .filter(Order.uid == customer.id, Order.status == "Paid")
            .scalar()
            or 0
        )

        customer_data.append(
            {
                "name": customer.name,
                "email": customer.email,
                "total_orders": total_orders,
                "total_spent": total_spent,
                "date_joined": getattr(customer, "date_joined", None),
            }
        )

    return render_template(
        "admin/customer_report.html",
        customers=customer_data,
        total_customers=len(customer_data),
    )


# ===============================
# ITEM MANAGEMENT (ADMIN TASK)
# ===============================


@admin.route("/items")
@admin_only
def items():

    items = Item.query.order_by(Item.id.desc()).all()

    return render_template("admin/items.html", items=items)


@admin.route("/items/add", methods=["GET", "POST"])
@admin_only
def add_item():

    form = AddItemForm()

    if form.validate_on_submit():
        image_file = form.image.data
        image_path = "app/static/uploads/" + image_file.filename
        image_file.save(image_path)

        image_url = url_for("static", filename=f"uploads/{image_file.filename}")

        item = Item(
            name=form.name.data,
            price=form.price.data,
            category=form.category.data,
            details=form.details.data,
            image=image_url,
            price_id=None,
        )

        db.session.add(item)
        db.session.commit()

        flash(f"{item.name} added successfully!", "success")

        return redirect(url_for("admin.items"))

    return render_template("admin/add.html", form=form)

from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash

from ..db_models import User
from . import admin
from .forms import AdminLoginForm


@admin.route("/login", methods=["GET", "POST"])
def login():
    
    if current_user.is_authenticated and current_user.admin:
        return redirect(url_for("admin.dashboard"))

    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if (
            user
            and user.admin
            and check_password_hash(user.password, form.password.data)
        ):
            login_user(user)
            return redirect(url_for("admin.dashboard"))
        flash("Invalid admin credentials", "error")
    return render_template("admin/login.html", form=form)


@admin.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("admin.login"))

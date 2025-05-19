from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

main = Blueprint("main", __name__)


@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("main/dashboard.html")


@main.route("/settings")
@login_required
def settings():
    return render_template("main/settings.html")

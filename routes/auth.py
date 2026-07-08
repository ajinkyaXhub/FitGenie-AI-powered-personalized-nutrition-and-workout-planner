from flask import Blueprint, render_template, redirect, url_for, request, flash
import traceback
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User
from utils.tokens import generate_reset_token, verify_reset_token
from utils.mailer import send_reset_email

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("meal.dashboard"))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Please fill in both username and password.", "danger")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            flash("Welcome back! Login successful.", "success")
            return redirect(url_for("meal.dashboard"))
        else:
            flash("Invalid username or password. Please try again.", "danger")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("meal.dashboard"))
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Basic validation
        if not username or not email or not password:
            flash("All fields are required to create an account.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose another one.", "warning")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("This email is already registered. Try logging in instead.", "warning")
            return redirect(url_for("auth.register"))

        try:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            print(f"[REGISTER ERROR] {type(e).__name__}: {e}")
            traceback.print_exc()
            flash(f"Registration error: {type(e).__name__}: {e}", "danger")
            return redirect(url_for("auth.register"))

    return render_template("register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("meal.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        user = User.query.filter_by(email=email).first()

        # Always show the same message whether or not the email exists,
        # so this form can't be used to check which emails are registered.
        if user:
            token = generate_reset_token(user.email)
            reset_url = url_for("auth.reset_password", token=token, _external=True)
            send_reset_email(user.email, reset_url)

        flash("If that email is registered, a reset link has been sent.", "success")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("meal.dashboard"))

    email = verify_reset_token(token)
    if not email:
        flash("That reset link is invalid or has expired. Please request a new one.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return redirect(url_for("auth.reset_password", token=token))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.reset_password", token=token))

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Account not found.", "danger")
            return redirect(url_for("auth.forgot_password"))

        user.set_password(password)
        db.session.commit()
        flash("Your password has been reset. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)
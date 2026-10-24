from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from backend.extensions import db, bcrypt
from backend.models import User
from backend.shared.utils import json_success, json_error

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login_page():
    return render_template("auth/login.html")


@auth_bp.get("/register")
def register_page():
    return render_template("auth/register.html")


@auth_bp.get("/forgot-password")
def forgot_password_page():
    return render_template("auth/forgot_password.html")


@auth_bp.post("/api/register")
def api_register():
    data = request.get_json(silent=True) or request.form or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if len(name) < 2 or not email or len(password) < 6:
        return json_error("Please provide a valid name, email, and password.", 400)
    if User.query.filter_by(email=email).first():
        return json_error("Email already registered.", 409)
    user = User(
        name=name,
        email=email,
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
        role="user",
    )
    db.session.add(user)
    db.session.commit()
    return json_success({"user": user.to_dict()}, "Registered successfully", 201)


@auth_bp.post("/api/login")
def api_login():
    data = request.get_json(silent=True) or request.form or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return json_error("Invalid credentials.", 401)
    access = create_access_token(identity=user.id, additional_claims={"role": user.role, "name": user.name})
    refresh = create_refresh_token(identity=user.id)
    return json_success({"access_token": access, "refresh_token": refresh, "user": user.to_dict()}, "Login successful")


@auth_bp.post("/api/refresh")
@jwt_required(refresh=True)
def api_refresh():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user:
        return json_error("User not found.", 404)
    access = create_access_token(identity=user.id, additional_claims={"role": user.role, "name": user.name})
    return json_success({"access_token": access}, "Token refreshed")


@auth_bp.post("/api/logout")
def api_logout():
    return json_success(message="Logged out")


@auth_bp.post("/api/forgot-password")
def api_forgot_password():
    return json_success(message="Password reset instructions sent to your email (mock)")


@auth_bp.post("/login")
def login_submit():
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        flash("Invalid credentials", "danger")
        return redirect(url_for("auth.login_page"))
    session["user_id"] = user.id
    session["name"] = user.name
    session["role"] = user.role
    flash("Welcome back to AasmaX!", "success")
    next_page = request.args.get("next") or url_for("storefront.home")
    return redirect(next_page)


@auth_bp.post("/register")
def register_submit():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    confirm = request.form.get("confirm_password") or ""
    if len(name) < 2:
        flash("Please enter your full name.", "danger")
        return redirect(url_for("auth.register_page"))
    if password != confirm:
        flash("Passwords do not match", "danger")
        return redirect(url_for("auth.register_page"))
    if User.query.filter_by(email=email).first():
        flash("Email already exists", "warning")
        return redirect(url_for("auth.register_page"))
    user = User(name=name, email=email, password_hash=bcrypt.generate_password_hash(password).decode("utf-8"), role="user")
    db.session.add(user)
    db.session.commit()
    flash("Account created. Please login.", "success")
    return redirect(url_for("auth.login_page"))


@auth_bp.post("/logout")
def logout_submit():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("storefront.home"))


@auth_bp.get("/profile")
def profile_page():
    return redirect(url_for("user.profile"))

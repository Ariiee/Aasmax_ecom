from functools import wraps
from flask import session, jsonify, redirect, url_for, request, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from backend.models import User


def session_user_id():
    value = session.get("user_id")
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def current_user():
    user_id = session_user_id()
    if user_id:
        return User.query.get(user_id)
    return None


def login_required_session(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session_user_id():
            return redirect(url_for("auth.login_page"))
        return fn(*args, **kwargs)
    return wrapper


def admin_required_session(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session_user_id():
            return redirect(url_for("admin.login_page"))
        if session.get("role") != "admin":
            return redirect(url_for("storefront.home"))
        return fn(*args, **kwargs)
    return wrapper


def jwt_user(optional=False):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if optional:
                try:
                    verify_jwt_in_request(optional=True)
                except Exception:
                    pass
            else:
                verify_jwt_in_request()
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def current_user_from_jwt():
    identity = get_jwt_identity()
    if not identity:
        return None
    return User.query.get(identity)


def require_logged_in_user():
    user = current_user()
    if user:
        return user
    identity = None
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
    except Exception:
        pass
    if identity:
        return User.query.get(identity)
    return None


def json_success(data=None, message="OK", status=200):
    payload = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status


def json_error(message="Request failed", status=400, **extra):
    payload = {"success": False, "message": message}
    payload.update(extra)
    return jsonify(payload), status


def money(value):
    try:
        return round(float(value or 0), 2)
    except (TypeError, ValueError):
        return 0.0

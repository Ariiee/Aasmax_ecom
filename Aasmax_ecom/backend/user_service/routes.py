from flask import Blueprint, render_template, session, request
from backend.extensions import db
from backend.models import User, Address, WishlistItem, Product, CartItem
from backend.shared.utils import json_success, json_error, login_required_session, session_user_id

user_bp = Blueprint("user", __name__)


def _current_user_id():
    return session_user_id()


def _request_data():
    return request.get_json(silent=True) or request.form or {}


@user_bp.get("/profile")
@login_required_session
def profile():
    user = User.query.get_or_404(_current_user_id())
    addresses = Address.query.filter_by(user_id=user.id).order_by(Address.is_default.desc(), Address.created_at.desc()).all()
    wishlist = WishlistItem.query.filter_by(user_id=user.id).all()
    cart_count = CartItem.query.filter_by(user_id=user.id).count()
    return render_template("store/profile.html", user=user, addresses=addresses, wishlist=wishlist, cart_count=cart_count)


@user_bp.put("/api/profile")
def api_update_profile():
    user_id = _current_user_id()
    if not user_id:
        return json_error("Login required", 401)
    data = _request_data()
    user = User.query.get_or_404(user_id)
    name = (data.get("name") or user.name).strip()
    email = (data.get("email") or user.email).strip().lower()
    if len(name) < 2:
        return json_error("Please provide a valid name.", 400)
    existing = User.query.filter(User.email == email, User.id != user.id).first()
    if existing:
        return json_error("Email already used by another account.", 409)
    user.name = name
    user.email = email
    db.session.commit()
    session["name"] = user.name
    return json_success({"user": user.to_dict()}, "Profile updated")


@user_bp.post("/api/addresses")
def api_add_address():
    user_id = _current_user_id()
    if not user_id:
        return json_error("Login required", 401)
    data = _request_data()
    required = ["line1", "city", "state", "postal_code"]
    if any(not (data.get(field) or "").strip() for field in required):
        return json_error("Please complete the address fields.", 400)
    address = Address(
        user_id=user_id,
        label=(data.get("label") or "Home").strip(),
        line1=data["line1"].strip(),
        line2=(data.get("line2") or "").strip() or None,
        city=data["city"].strip(),
        state=data["state"].strip(),
        postal_code=data["postal_code"].strip(),
        country=(data.get("country") or "India").strip(),
        is_default=bool(data.get("is_default")),
    )
    if address.is_default:
        Address.query.filter_by(user_id=user_id, is_default=True).update({"is_default": False})
    elif not Address.query.filter_by(user_id=user_id).count():
        address.is_default = True
    db.session.add(address)
    db.session.commit()
    return json_success({"address": address.to_dict()}, "Address added", 201)


@user_bp.put("/api/addresses/<int:address_id>")
def api_update_address(address_id):
    user_id = _current_user_id()
    if not user_id:
        return json_error("Login required", 401)
    address = Address.query.get_or_404(address_id)
    if address.user_id != user_id:
        return json_error("Forbidden", 403)
    data = _request_data()
    address.label = (data.get("label") or address.label).strip()
    address.line1 = (data.get("line1") or address.line1).strip()
    address.line2 = (data.get("line2") or address.line2 or "").strip() or None
    address.city = (data.get("city") or address.city).strip()
    address.state = (data.get("state") or address.state).strip()
    address.postal_code = (data.get("postal_code") or address.postal_code).strip()
    address.country = (data.get("country") or address.country).strip()
    make_default = bool(data.get("is_default"))
    if make_default:
        Address.query.filter_by(user_id=user_id, is_default=True).update({"is_default": False})
        address.is_default = True
    db.session.commit()
    return json_success({"address": address.to_dict()}, "Address updated")


@user_bp.delete("/api/addresses/<int:address_id>")
def api_delete_address(address_id):
    user_id = _current_user_id()
    if not user_id:
        return json_error("Login required", 401)
    address = Address.query.get_or_404(address_id)
    if address.user_id != user_id:
        return json_error("Forbidden", 403)
    db.session.delete(address)
    db.session.commit()
    return json_success(message="Address removed")


@user_bp.post("/api/wishlist")
def api_add_wishlist():
    data = _request_data()
    user_id = _current_user_id()
    product_id = data.get("product_id")
    if not user_id:
        return json_error("Login required", 401)
    if not product_id:
        return json_error("product_id is required", 400)
    item = WishlistItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not item:
        item = WishlistItem(user_id=user_id, product_id=product_id)
        db.session.add(item)
        db.session.commit()
    return json_success(message="Added to wishlist", status=201)


@user_bp.delete("/api/wishlist")
def api_remove_wishlist():
    data = _request_data()
    user_id = _current_user_id()
    product_id = data.get("product_id")
    if not user_id:
        return json_error("Login required", 401)
    if not product_id:
        return json_error("product_id is required", 400)
    item = WishlistItem.query.filter_by(user_id=user_id, product_id=product_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return json_success(message="Removed from wishlist")


@user_bp.post("/api/wishlist/move-to-cart")
def api_move_wishlist_to_cart():
    data = _request_data()
    user_id = _current_user_id()
    if not user_id:
        return json_error("Login required", 401)
    product_id = data.get("product_id")
    if not product_id:
        return json_error("product_id is required", 400)
    wishlist_item = WishlistItem.query.filter_by(user_id=user_id, product_id=product_id).first_or_404()
    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += int(data.get("quantity", 1))
    else:
        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=int(data.get("quantity", 1)))
        db.session.add(cart_item)
    db.session.delete(wishlist_item)
    db.session.commit()
    return json_success({"cart_item": cart_item.to_dict()}, "Moved to cart")

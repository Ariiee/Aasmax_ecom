from flask import Blueprint, request, session, redirect, url_for, render_template
from backend.extensions import db
from backend.models import CartItem, Product
from backend.shared.utils import json_success, json_error, login_required_session, session_user_id

cart_bp = Blueprint("cart", __name__)


def _current_user_id():
    return session_user_id()


def _request_data():
    return request.get_json(silent=True) or request.form or {}


@cart_bp.get("/cart")
@login_required_session
def cart_page():
    items = CartItem.query.filter_by(user_id=_current_user_id()).all()
    subtotal = round(sum(item.quantity * item.product.price for item in items), 2)
    shipping_fee = 0 if subtotal >= 999 else (49 if items else 0)
    tax = round(subtotal * 0.05, 2)
    total = round(subtotal + shipping_fee + tax, 2)
    return render_template("store/cart.html", items=items, subtotal=subtotal, shipping_fee=shipping_fee, tax=tax, total=total)


@cart_bp.post("/api/cart/items")
def add_to_cart():
    data = _request_data()
    user_id = _current_user_id()
    if not user_id:
        return json_error("Login required", 401)
    product_id = data.get("product_id")
    if not product_id:
        return json_error("product_id is required", 400)
    product = Product.query.get_or_404(product_id)
    qty = max(1, int(data.get("quantity", 1)))
    item = CartItem.query.filter_by(user_id=user_id, product_id=product.id).first()
    if item:
        item.quantity += qty
    else:
        item = CartItem(user_id=user_id, product_id=product.id, quantity=qty)
        db.session.add(item)
    db.session.commit()
    return json_success({"cart_item": item.to_dict(), "cart_count": CartItem.query.filter_by(user_id=user_id).count()}, "Added to cart", 201)


@cart_bp.put("/api/cart/items/<int:item_id>")
def update_cart_item(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != _current_user_id():
        return json_error("Forbidden", 403)
    data = _request_data()
    quantity = int(data.get("quantity", 1))
    if quantity < 1:
        return json_error("Quantity must be at least 1.", 400)
    item.quantity = quantity
    db.session.commit()
    return json_success({"cart_item": item.to_dict()}, "Cart updated")


@cart_bp.delete("/api/cart/items/<int:item_id>")
def delete_cart_item(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != _current_user_id():
        return json_error("Forbidden", 403)
    db.session.delete(item)
    db.session.commit()
    return json_success(message="Item removed")


@cart_bp.get("/api/cart")
def get_cart():
    user_id = _current_user_id() or request.args.get("user_id")
    if not user_id:
        return json_success({"items": [], "subtotal": 0}, "Empty cart")
    items = CartItem.query.filter_by(user_id=user_id).all()
    payload = [i.to_dict() for i in items]
    subtotal = round(sum(item["line_total"] for item in payload), 2)
    shipping_fee = 0 if subtotal >= 999 else (49 if payload else 0)
    tax = round(subtotal * 0.05, 2)
    total = round(subtotal + shipping_fee + tax, 2)
    return json_success({"items": payload, "subtotal": subtotal, "shipping_fee": shipping_fee, "tax": tax, "total": total})

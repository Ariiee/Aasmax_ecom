import uuid
from flask import Blueprint, request, session, render_template, redirect, url_for
from backend.extensions import db
from backend.models import CartItem, Order, OrderItem, Address, Product, User
from backend.shared.utils import json_success, json_error, login_required_session, session_user_id

order_bp = Blueprint("order", __name__)


def _current_user_id():
    return session_user_id()


def _calculate_totals(cart_items):
    subtotal = round(sum(item.product.price * item.quantity for item in cart_items), 2)
    shipping_fee = 0 if subtotal >= 999 else (49 if cart_items else 0)
    tax = round(subtotal * 0.05, 2)
    total = round(subtotal + shipping_fee + tax, 2)
    return subtotal, shipping_fee, tax, total


def _build_checkout_context(user_id):
    user = User.query.get_or_404(user_id)
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    addresses = Address.query.filter_by(user_id=user_id).order_by(Address.is_default.desc(), Address.created_at.desc()).all()
    subtotal, shipping_fee, tax, total = _calculate_totals(cart_items)
    return {
        "user": user,
        "cart_items": cart_items,
        "addresses": addresses,
        "subtotal": subtotal,
        "shipping_fee": shipping_fee,
        "tax": tax,
        "total": total,
    }


@order_bp.get("/checkout")
@login_required_session
def checkout_page():
    return render_template("store/checkout.html", **_build_checkout_context(_current_user_id()))


@order_bp.post("/checkout/place")
@login_required_session
def place_order_form():
    payload = request.form.to_dict(flat=True)
    result = _create_order(_current_user_id(), payload)
    if isinstance(result, tuple):
        message, status = result
        return render_template("store/checkout.html", **_build_checkout_context(_current_user_id()), error=message), status
    return redirect(url_for("order.order_detail_page", order_id=result.id))


@order_bp.get("/orders")
@login_required_session
def order_history_page():
    orders = Order.query.filter_by(user_id=_current_user_id()).order_by(Order.created_at.desc()).all()
    return render_template("store/orders.html", orders=orders)


@order_bp.get("/orders/<int:order_id>")
@login_required_session
def order_detail_page(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != _current_user_id():
        return redirect(url_for("order.order_history_page"))
    return render_template("store/order_detail.html", order=order)


def _create_order(user_id, data):
    if not user_id:
        return "Login required", 401
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return "Your cart is empty.", 400

    address = None
    address_id = data.get("address_id")
    if address_id:
        address = Address.query.filter_by(id=address_id, user_id=user_id).first()
    elif data.get("address_line1"):
        address = {
            "label": data.get("address_label") or "Shipping",
            "line1": data.get("address_line1"),
            "line2": data.get("address_line2") or None,
            "city": data.get("address_city"),
            "state": data.get("address_state"),
            "postal_code": data.get("address_postal_code"),
            "country": data.get("address_country") or "India",
            "is_default": False,
        }
    else:
        address = Address.query.filter_by(user_id=user_id, is_default=True).first() or Address.query.filter_by(user_id=user_id).first()

    if not address:
        return "Please select or add a shipping address.", 400

    for item in cart_items:
        if item.quantity > item.product.stock:
            return f"Not enough stock for {item.product.name}.", 400

    subtotal, shipping_fee, tax, total = _calculate_totals(cart_items)
    payment_method = (data.get("payment_method") or "cod").lower()
    if payment_method not in {"cod", "mockpay"}:
        payment_method = "cod"

    order = Order(
        order_number=f"ORD-{uuid.uuid4().hex[:10].upper()}",
        user_id=user_id,
        status="pending",
        payment_status="pending",
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        tax=tax,
        total=total,
        address_snapshot=address.to_dict() if hasattr(address, "to_dict") else address,
        payment_method=payment_method,
    )
    db.session.add(order)
    db.session.flush()

    for item in cart_items:
        db.session.add(OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            product_name=item.product.name,
            unit_price=item.product.price,
            quantity=item.quantity,
        ))
        item.product.stock = max(0, item.product.stock - item.quantity)

    if payment_method == "mockpay":
        order.payment_status = "paid"
        order.status = "confirmed"
        from backend.payment_service.routes import create_mock_payment
        create_mock_payment(order)
    elif payment_method == "cod":
        order.status = "confirmed"
        order.payment_status = "pending"

    for item in cart_items:
        db.session.delete(item)

    db.session.commit()
    return order


@order_bp.post("/api/orders/checkout")
def checkout():
    data = request.get_json(silent=True) or request.form or {}
    result = _create_order(_current_user_id(), data)
    if isinstance(result, tuple):
        message, status = result
        return json_error(message, status)
    return json_success({"order": result.to_dict()}, "Checkout complete", 201)


@order_bp.get("/api/orders")
def api_orders():
    user_id = _current_user_id() or request.args.get("user_id")
    if not user_id:
        return json_success({"orders": []})
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return json_success({"orders": [o.to_dict() for o in orders]})


@order_bp.put("/api/orders/<int:order_id>/status")
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json(force=True)
    status = data.get("status")
    if status not in {"pending", "confirmed", "shipped", "delivered", "cancelled"}:
        return json_error("Invalid status", 400)
    order.status = status
    if status == "cancelled":
        order.payment_status = "refunded" if order.payment_status == "paid" else order.payment_status
    db.session.commit()
    return json_success({"order": order.to_dict()}, "Order status updated")

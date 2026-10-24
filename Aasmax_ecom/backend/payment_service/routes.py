import uuid
from flask import Blueprint, request
from backend.extensions import db
from backend.models import Payment, Order
from backend.shared.utils import json_success, json_error

payment_bp = Blueprint("payment", __name__)


def create_mock_payment(order):
    ref = f"MOCK-{uuid.uuid4().hex[:12].upper()}"
    payment = Payment(order_id=order.id, provider="mockpay", status="paid", transaction_ref=ref, amount=order.total)
    db.session.add(payment)
    order.payment_status = "paid"
    order.status = "confirmed"
    return payment


@payment_bp.post("/api/payments/mock-initiate")
def mock_initiate_payment():
    data = request.get_json(force=True)
    order = Order.query.get_or_404(data["order_id"])
    ref = f"MOCK-{uuid.uuid4().hex[:12].upper()}"
    payment = Payment(order_id=order.id, provider="mockpay", status="paid", transaction_ref=ref, amount=order.total)
    db.session.add(payment)
    order.payment_status = "initiated"
    db.session.commit()
    return json_success({"transaction_ref": ref, "amount": order.total}, "Payment initiated", 201)


@payment_bp.post("/api/payments/mock-confirm")
def mock_confirm_payment():
    data = request.get_json(force=True)
    payment = Payment.query.filter_by(transaction_ref=data["transaction_ref"]).first_or_404()
    payment.status = "paid"
    payment.order.payment_status = "paid"
    payment.order.status = "confirmed"
    db.session.commit()
    return json_success({"payment": {"transaction_ref": payment.transaction_ref, "status": payment.status}}, "Payment confirmed")

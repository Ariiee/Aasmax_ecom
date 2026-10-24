from flask import Blueprint, request
from backend.extensions import db
from backend.models import Order
from backend.shared.utils import json_success

notification_bp = Blueprint("notification", __name__)

@notification_bp.post("/api/notifications/order-status")
def notify_order_status():
    data = request.get_json(force=True)
    order = Order.query.get_or_404(data["order_id"])
    message = data.get("message") or f"Order {order.order_number} is now {order.status}"
    # In real life this would dispatch email/SMS/push notification.
    return json_success({"order_number": order.order_number, "message": message}, "Notification queued")

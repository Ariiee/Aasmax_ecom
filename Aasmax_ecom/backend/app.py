import os
from pathlib import Path
from flask import Flask, session
from sqlalchemy import func
from dotenv import load_dotenv
from backend.config import DevelopmentConfig
from backend.extensions import db, bcrypt, jwt, cors, migrate
from backend.shared.errors import register_error_handlers
from backend.shared.logging_config import configure_logging
from backend.shared.utils import current_user, session_user_id
from backend.auth_service.routes import auth_bp
from backend.product_service.routes import storefront_bp, product_api_bp
from backend.cart_service.routes import cart_bp
from backend.order_service.routes import order_bp
from backend.payment_service.routes import payment_bp
from backend.user_service.routes import user_bp
from backend.admin_service.routes import admin_bp
from backend.notification_service.routes import notification_bp
from backend.models import CartItem, WishlistItem

load_dotenv()

APP_NAME = "AasmaX"


def create_app(config_object=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_object or DevelopmentConfig)
    if os.getenv("DATABASE_URL"):
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)

    configure_logging(app)
    register_error_handlers(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(storefront_bp)
    app.register_blueprint(product_api_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notification_bp)

    @app.context_processor
    def inject_globals():
        user = current_user()
        user_id = session_user_id()
        cart_count = 0
        wishlist_count = 0
        if user_id:
            cart_count = db.session.query(func.coalesce(func.sum(CartItem.quantity), 0)).filter(CartItem.user_id == user_id).scalar() or 0
            wishlist_count = WishlistItem.query.filter_by(user_id=user_id).count()
        return {
            "app_name": APP_NAME,
            "current_user": user,
            "cart_count": int(cart_count),
            "wishlist_count": int(wishlist_count),
        }

    @app.get("/health")
    def health():
        return {"status": "ok", "app": APP_NAME}

    @app.route("/api")
    def api_root():
        return {"message": f"{APP_NAME} API is running"}

    return app

from datetime import datetime
from backend.extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(db.Model, TimestampMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    addresses = db.relationship("Address", backref="user", lazy=True, cascade="all, delete-orphan")
    cart_items = db.relationship("CartItem", backref="user", lazy=True, cascade="all, delete-orphan")
    wishlist_items = db.relationship("WishlistItem", backref="user", lazy=True, cascade="all, delete-orphan")
    orders = db.relationship("Order", backref="user", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
        }


class Address(db.Model, TimestampMixin):
    __tablename__ = "addresses"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    label = db.Column(db.String(80), nullable=False, default="Home")
    line1 = db.Column(db.String(255), nullable=False)
    line2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False, default="India")
    is_default = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "line1": self.line1,
            "line2": self.line2,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
            "is_default": self.is_default,
        }


class Category(db.Model, TimestampMixin):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    slug = db.Column(db.String(140), unique=True, nullable=False, index=True)
    products = db.relationship("Product", backref="category", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "slug": self.slug}


class Product(db.Model, TimestampMixin):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    compare_at_price = db.Column(db.Float, nullable=True)
    stock = db.Column(db.Integer, default=0, nullable=False)
    image_url = db.Column(db.String(300), nullable=True)
    gallery_images = db.Column(db.JSON, nullable=True)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    reviews = db.relationship("Review", backref="product", lazy=True, cascade="all, delete-orphan")
    cart_items = db.relationship("CartItem", backref="product", lazy=True, cascade="all, delete-orphan")
    wishlist_items = db.relationship("WishlistItem", backref="product", lazy=True, cascade="all, delete-orphan")
    order_items = db.relationship("OrderItem", backref="product", lazy=True)

    def to_dict(self):
        gallery = self.gallery_images or []
        if self.image_url and self.image_url not in gallery:
            gallery = [self.image_url, *gallery]
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "price": self.price,
            "compare_at_price": self.compare_at_price,
            "stock": self.stock,
            "image_url": self.image_url,
            "gallery_images": gallery,
            "featured": self.featured,
            "category": self.category.to_dict() if self.category else None,
        }


class Review(db.Model, TimestampMixin):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)


class CartItem(db.Model, TimestampMixin):
    __tablename__ = "cart_items"
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "quantity": self.quantity,
            "product": self.product.to_dict(),
            "line_total": round(self.quantity * self.product.price, 2),
        }


class WishlistItem(db.Model, TimestampMixin):
    __tablename__ = "wishlist_items"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)


class Order(db.Model, TimestampMixin):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(40), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(30), default="pending", nullable=False)
    payment_status = db.Column(db.String(30), default="pending", nullable=False)
    subtotal = db.Column(db.Float, nullable=False, default=0)
    shipping_fee = db.Column(db.Float, nullable=False, default=0)
    tax = db.Column(db.Float, nullable=False, default=0)
    total = db.Column(db.Float, nullable=False, default=0)
    address_snapshot = db.Column(db.JSON, nullable=True)
    payment_method = db.Column(db.String(40), nullable=False, default="cod")

    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")
    payment = db.relationship("Payment", backref="order", uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "order_number": self.order_number,
            "status": self.status,
            "payment_status": self.payment_status,
            "subtotal": self.subtotal,
            "shipping_fee": self.shipping_fee,
            "tax": self.tax,
            "total": self.total,
            "payment_method": self.payment_method,
            "address_snapshot": self.address_snapshot,
            "items": [item.to_dict() for item in self.items],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class OrderItem(db.Model, TimestampMixin):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "product_name": self.product_name,
            "unit_price": self.unit_price,
            "quantity": self.quantity,
            "line_total": round(self.unit_price * self.quantity, 2),
        }


class Payment(db.Model, TimestampMixin):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, unique=True)
    provider = db.Column(db.String(50), nullable=False, default="mockpay")
    status = db.Column(db.String(30), nullable=False, default="initiated")
    transaction_ref = db.Column(db.String(120), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)


class Banner(db.Model, TimestampMixin):
    __tablename__ = "banners"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    subtitle = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(300), nullable=True)
    cta_text = db.Column(db.String(50), nullable=True)
    cta_link = db.Column(db.String(200), nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

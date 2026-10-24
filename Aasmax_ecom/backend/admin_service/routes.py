from flask import Blueprint, render_template, session, request, redirect, url_for
from sqlalchemy import func
from backend.extensions import db, bcrypt
from backend.models import User, Product, Order, Category, Banner
from backend.shared.utils import admin_required_session, json_success

admin_bp = Blueprint("admin", __name__)


def _parse_gallery(value):
    if not value:
        return []
    return [item.strip() for item in str(value).replace("\n", ",").split(",") if item.strip()]


@admin_bp.get("/admin/login")
def login_page():
    return render_template("admin/login.html")


@admin_bp.post("/admin/login")
def login_submit():
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    user = User.query.filter_by(email=email, role="admin").first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return render_template("admin/login.html", error="Invalid admin credentials")
    session["user_id"] = user.id
    session["name"] = user.name
    session["role"] = user.role
    return redirect(url_for("admin.dashboard"))


@admin_bp.post("/admin/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login_page"))


@admin_bp.get("/admin")
@admin_required_session
def dashboard():
    total_revenue = db.session.query(func.coalesce(func.sum(Order.total), 0)).scalar()
    total_orders = Order.query.count()
    total_users = User.query.filter_by(role="user").count()
    products = Product.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    sales_by_status = db.session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    return render_template(
        "admin/dashboard.html",
        total_revenue=round(total_revenue, 2),
        total_orders=total_orders,
        total_users=total_users,
        products=products,
        recent_orders=recent_orders,
        sales_by_status=sales_by_status,
    )


@admin_bp.get("/admin/products")
@admin_required_session
def products_page():
    products = Product.query.order_by(Product.created_at.desc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("admin/products.html", products=products, categories=categories)


@admin_bp.get("/admin/products/new")
@admin_required_session
def product_new_page():
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("admin/product_form.html", categories=categories, product=None)


@admin_bp.get("/admin/products/<int:product_id>/edit")
@admin_required_session
def product_edit_page(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("admin/product_form.html", categories=categories, product=product)


@admin_bp.post("/admin/products")
@admin_required_session
def create_product_form():
    from werkzeug.utils import secure_filename
    from flask import current_app
    import os
    from uuid import uuid4

    name = (request.form.get("name") or "").strip()
    slug = (request.form.get("slug") or "").strip()
    description = (request.form.get("description") or "").strip()
    category_id = int(request.form.get("category_id"))
    image = request.files.get("image")
    image_url = (request.form.get("image_url") or "").strip() or None
    gallery_images = _parse_gallery(request.form.get("gallery_images"))

    if image and image.filename:
        filename = f"{uuid4().hex}_{secure_filename(image.filename)}"
        upload_dir = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_dir, exist_ok=True)
        image.save(os.path.join(upload_dir, filename))
        image_url = f"/static/uploads/{filename}"

    category = Category.query.get_or_404(category_id)
    product = Product(
        name=name,
        slug=slug,
        description=description,
        price=float(request.form.get("price") or 0),
        compare_at_price=float(request.form.get("compare_at_price") or 0) or None,
        stock=int(request.form.get("stock") or 0),
        image_url=image_url or "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1200&q=80",
        gallery_images=gallery_images,
        featured=bool(request.form.get("featured")),
        category=category,
    )
    db.session.add(product)
    db.session.commit()
    return redirect(url_for("admin.products_page"))


@admin_bp.post("/admin/products/<int:product_id>/edit")
@admin_required_session
def update_product_form(product_id):
    product = Product.query.get_or_404(product_id)
    product.name = (request.form.get("name") or product.name).strip()
    product.slug = (request.form.get("slug") or product.slug).strip()
    product.description = (request.form.get("description") or product.description).strip()
    product.price = float(request.form.get("price") or product.price)
    product.compare_at_price = float(request.form.get("compare_at_price") or 0) or None
    product.stock = int(request.form.get("stock") or product.stock)
    product.featured = bool(request.form.get("featured"))
    product.gallery_images = _parse_gallery(request.form.get("gallery_images"))
    if request.form.get("category_id"):
        product.category = Category.query.get_or_404(int(request.form.get("category_id")))
    image_url = (request.form.get("image_url") or "").strip()
    if image_url:
        product.image_url = image_url
    db.session.commit()
    return redirect(url_for("admin.products_page"))


@admin_bp.post("/admin/products/<int:product_id>/delete")
@admin_required_session
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("admin.products_page"))


@admin_bp.get("/admin/orders")
@admin_required_session
def orders_page():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", orders=orders)


@admin_bp.post("/admin/orders/<int:order_id>/status")
@admin_required_session
def update_status(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.form.get("status")
    if status in {"pending", "confirmed", "shipped", "delivered", "cancelled"}:
        order.status = status
        db.session.commit()
    return redirect(url_for("admin.orders_page"))


@admin_bp.get("/admin/users")
@admin_required_session
def users_page():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


@admin_bp.get("/admin/content")
@admin_required_session
def content_page():
    banners = Banner.query.order_by(Banner.sort_order.asc()).all()
    return render_template("admin/content.html", banners=banners)


@admin_bp.post("/admin/banners")
@admin_required_session
def create_banner():
    banner = Banner(
        title=request.form.get("title"),
        subtitle=request.form.get("subtitle"),
        image_url=request.form.get("image_url"),
        cta_text=request.form.get("cta_text"),
        cta_link=request.form.get("cta_link"),
        active=bool(request.form.get("active")),
        sort_order=int(request.form.get("sort_order") or 0),
    )
    db.session.add(banner)
    db.session.commit()
    return redirect(url_for("admin.content_page"))


@admin_bp.get("/admin/api/analytics")
@admin_required_session
def analytics_api():
    revenue = float(db.session.query(func.coalesce(func.sum(Order.total), 0)).scalar() or 0)
    user_count = User.query.count()
    product_count = Product.query.count()
    order_count = Order.query.count()
    return json_success({
        "revenue": revenue,
        "users": user_count,
        "products": product_count,
        "orders": order_count,
    })

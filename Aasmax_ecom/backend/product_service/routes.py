from flask import Blueprint, render_template, request
from sqlalchemy import or_
from backend.extensions import db
from backend.models import Product, Category, Review, Banner
from backend.shared.utils import json_success, json_error

storefront_bp = Blueprint("storefront", __name__)
product_api_bp = Blueprint("product_api", __name__)


@storefront_bp.get("/")
def home():
    featured = Product.query.filter_by(featured=True).order_by(Product.created_at.desc()).limit(8).all()
    categories = Category.query.order_by(Category.name.asc()).all()
    banners = Banner.query.filter_by(active=True).order_by(Banner.sort_order.asc()).all()
    products = Product.query.order_by(Product.created_at.desc()).limit(12).all()
    return render_template("store/home.html", featured=featured, categories=categories, banners=banners, products=products)


@storefront_bp.get("/products")
def catalog():
    q = (request.args.get("q") or "").strip()
    category = request.args.get("category")
    query = Product.query
    if q:
        query = query.filter(or_(Product.name.ilike(f"%{q}%"), Product.description.ilike(f"%{q}%")))
    if category:
        query = query.join(Category).filter(Category.slug == category)
    products = query.order_by(Product.created_at.desc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("store/catalog.html", products=products, categories=categories, q=q, selected_category=category)


@storefront_bp.get("/product/<slug>")
def product_detail(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    return render_template("store/product_detail.html", product=product)


@product_api_bp.get("/api/products")
def api_list_products():
    q = (request.args.get("q") or "").strip()
    category = request.args.get("category")
    query = Product.query
    if q:
        query = query.filter(or_(Product.name.ilike(f"%{q}%"), Product.description.ilike(f"%{q}%")))
    if category:
        query = query.join(Category).filter(Category.slug == category)
    products = query.order_by(Product.created_at.desc()).all()
    return json_success({"products": [p.to_dict() for p in products]})


@product_api_bp.get("/api/products/<slug>")
def api_product_detail(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    return json_success({"product": product.to_dict()})


@product_api_bp.post("/api/products")
def api_create_product():
    data = request.get_json(force=True)
    category = Category.query.filter_by(slug=data["category_slug"]).first()
    if not category:
        return json_error("Category not found", 404)
    product = Product(
        name=data["name"],
        slug=data["slug"],
        description=data["description"],
        price=data["price"],
        compare_at_price=data.get("compare_at_price"),
        stock=data.get("stock", 0),
        image_url=data.get("image_url"),
        gallery_images=data.get("gallery_images") or [],
        featured=bool(data.get("featured", False)),
        category=category,
    )
    db.session.add(product)
    db.session.commit()
    return json_success({"product": product.to_dict()}, "Product created", 201)


@product_api_bp.put("/api/products/<int:product_id>")
def api_update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json(force=True)
    for field in ["name", "slug", "description", "image_url"]:
        if field in data:
            setattr(product, field, data[field])
    for field in ["price", "compare_at_price", "stock", "featured"]:
        if field in data:
            setattr(product, field, data[field])
    if "gallery_images" in data:
        product.gallery_images = data.get("gallery_images") or []
    if "category_slug" in data:
        category = Category.query.filter_by(slug=data["category_slug"]).first()
        if category:
            product.category = category
    db.session.commit()
    return json_success({"product": product.to_dict()}, "Product updated")


@product_api_bp.delete("/api/products/<int:product_id>")
def api_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return json_success(message="Product deleted")


@product_api_bp.get("/api/categories")
def api_categories():
    categories = Category.query.order_by(Category.name.asc()).all()
    return json_success({"categories": [c.to_dict() for c in categories]})


@product_api_bp.post("/api/reviews")
def api_create_review():
    data = request.get_json(force=True)
    review = Review(
        user_id=data["user_id"],
        product_id=data["product_id"],
        rating=data["rating"],
        comment=data.get("comment"),
    )
    db.session.add(review)
    db.session.commit()
    return json_success(message="Review added", status=201)

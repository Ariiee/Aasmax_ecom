from backend.app import create_app
from backend.extensions import db, bcrypt
from backend.models import User, Category, Product, Banner, Address, Review

app = create_app()


def seed():
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(email="admin@demo.com").first():
            admin = User(
                name="Admin",
                email="admin@demo.com",
                password_hash=bcrypt.generate_password_hash("Admin@123").decode("utf-8"),
                role="admin",
            )
            user = User(
                name="Demo User",
                email="user@demo.com",
                password_hash=bcrypt.generate_password_hash("User@123").decode("utf-8"),
                role="user",
            )
            db.session.add_all([admin, user])
            db.session.commit()

        electronics = Category.query.filter_by(slug="electronics").first()
        fashion = Category.query.filter_by(slug="fashion").first()
        home = Category.query.filter_by(slug="home-living").first()
        if not electronics:
            electronics = Category(name="Electronics", slug="electronics")
            fashion = Category(name="Fashion", slug="fashion")
            home = Category(name="Home & Living", slug="home-living")
            db.session.add_all([electronics, fashion, home])
            db.session.commit()

        if Product.query.count() == 0:
            products = [
                Product(
                    name="Nebula X Headphones",
                    slug="nebula-x-headphones",
                    description="Premium ANC headphones with spatial audio and 40h battery.",
                    price=4999,
                    compare_at_price=6999,
                    stock=40,
                    featured=True,
                    image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1200&q=80",
                    gallery_images=[
                        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1200&q=80",
                        "https://images.unsplash.com/photo-1518441902117-f0a0cf7b8c97?auto=format&fit=crop&w=1200&q=80",
                    ],
                    category=electronics,
                ),
                Product(
                    name="Aero Smart Watch",
                    slug="aero-smart-watch",
                    description="Fitness tracking, calls, notifications, and AMOLED display.",
                    price=7999,
                    compare_at_price=9999,
                    stock=25,
                    featured=True,
                    image_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1200&q=80",
                    gallery_images=[
                        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1200&q=80",
                        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=1200&q=80",
                    ],
                    category=electronics,
                ),
                Product(
                    name="Urban Sneaker",
                    slug="urban-sneaker",
                    description="Comfort-first daily sneaker with breathable knit upper.",
                    price=2499,
                    compare_at_price=3299,
                    stock=60,
                    featured=False,
                    image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=1200&q=80",
                    gallery_images=[
                        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=1200&q=80",
                        "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?auto=format&fit=crop&w=1200&q=80",
                    ],
                    category=fashion,
                ),
                Product(
                    name="Luna Desk Lamp",
                    slug="luna-desk-lamp",
                    description="Minimal LED lamp with warm-to-cool lighting presets.",
                    price=1499,
                    compare_at_price=1999,
                    stock=50,
                    featured=True,
                    image_url="https://images.unsplash.com/photo-1517705008128-361805f42e86?auto=format&fit=crop&w=1200&q=80",
                    gallery_images=[
                        "https://images.unsplash.com/photo-1517705008128-361805f42e86?auto=format&fit=crop&w=1200&q=80",
                        "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=1200&q=80",
                    ],
                    category=home,
                ),
            ]
            db.session.add_all(products)
            db.session.commit()

        if Banner.query.count() == 0:
            banners = [
                Banner(
                    title="New Season Collection",
                    subtitle="Launch-ready storefronts for modern brands.",
                    image_url="https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=1600&q=80",
                    cta_text="Shop Now",
                    cta_link="/products",
                    active=True,
                    sort_order=1,
                ),
                Banner(
                    title="Premium Admin Dashboard",
                    subtitle="Track revenue, orders, and customers in one view.",
                    image_url="https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1600&q=80",
                    cta_text="Admin Login",
                    cta_link="/admin/login",
                    active=True,
                    sort_order=2,
                ),
            ]
            db.session.add_all(banners)
            db.session.commit()

        user = User.query.filter_by(email="user@demo.com").first()
        if user and not user.addresses:
            db.session.add(Address(
                user_id=user.id, label="Home", line1="12 Lake View Road",
                line2="Apt 4B", city="Kolkata", state="West Bengal",
                postal_code="700001", country="India", is_default=True,
            ))
            db.session.commit()


if __name__ == "__main__":
    seed()
    print("Database seeded.")

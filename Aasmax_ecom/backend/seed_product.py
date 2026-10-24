import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from backend.app import create_app, db
from backend.models import Product, Category
from slugify import slugify

app = create_app()

with app.app_context():

    # ✅ Ensure categories exist
    categories = {
        "Footwear": 1,
        "Clothing": 2,
        "Electronics": 3,
        "Accessories": 4,
        "Home": 5,
        "Fitness": 6,
    }

    # Create categories if not exist
    for name in categories.keys():
        existing = Category.query.filter_by(name=name).first()
        if not existing:
            cat = Category(name=name, slug=slugify(name))
            db.session.add(cat)

    db.session.commit()

    # Refresh category IDs
    category_map = {c.name: c.id for c in Category.query.all()}

    products_data = [
        ("Nike Air Sneakers", 3499, "Stylish sneakers", "https://images.unsplash.com/photo-1542291026-7eec264c27ff", "Footwear"),
        ("Running Shoes", 2599, "Lightweight shoes", "https://images.unsplash.com/photo-1528701800489-20be3c3d1d6c", "Footwear"),
        ("Men Hoodie", 1499, "Warm hoodie", "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf", "Clothing"),
        ("Denim Jacket", 2999, "Classic jacket", "https://images.unsplash.com/photo-1520975922284-9e0ce827c27b", "Clothing"),
        ("Smart Watch", 4999, "Fitness watch", "https://images.unsplash.com/photo-1516574187841-cb9cc2ca948b", "Electronics"),
        ("Bluetooth Speaker", 1999, "Portable speaker", "https://images.unsplash.com/photo-1585386959984-a4155224a1ad", "Electronics"),
        ("Laptop", 55999, "High performance", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8", "Electronics"),
        ("Gaming Mouse", 1499, "RGB mouse", "https://images.unsplash.com/photo-1587202372775-e229f172b9d7", "Electronics"),
        ("Leather Wallet", 999, "Premium wallet", "https://images.unsplash.com/photo-1511499767150-a48a237f0083", "Accessories"),
        ("Backpack", 2499, "Travel bag", "https://images.unsplash.com/photo-1506744038136-46273834b3fb", "Accessories"),
        ("Table Lamp", 1799, "Modern lamp", "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85", "Home"),
        ("Wall Clock", 899, "Minimal clock", "https://images.unsplash.com/photo-1503387762-592deb58ef4e", "Home"),
        ("Chair", 3499, "Ergonomic chair", "https://images.unsplash.com/photo-1503602642458-232111445657", "Home"),
        ("Smartphone", 24999, "Android phone", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9", "Electronics"),
        ("Tablet", 19999, "Portable tablet", "https://images.unsplash.com/photo-1587829741301-dc798b83add3", "Electronics"),
        ("Power Bank", 1299, "10000mAh", "https://images.unsplash.com/photo-1580910051074-3eb694886505", "Electronics"),
        ("Dumbbells", 1999, "Gym set", "https://images.unsplash.com/photo-1599058917212-d750089bc07e", "Fitness"),
        ("Yoga Mat", 999, "Non-slip mat", "https://images.unsplash.com/photo-1552196563-55cd4e45efb3", "Fitness"),
        ("Treadmill", 29999, "Home treadmill", "https://images.unsplash.com/photo-1579758629938-03607ccdbaba", "Fitness"),
    ]

    for name, price, desc, img, cat in products_data:
        product = Product(
            name=name,
            slug=slugify(name),
            description=desc,
            price=price,
            compare_at_price=price + 500,
            stock=50,
            image_url=img,
            gallery_images=[img],
            featured=True,
            category_id=category_map[cat]
        )
        db.session.add(product)

    db.session.commit()

    print("✅ Products inserted successfully!")
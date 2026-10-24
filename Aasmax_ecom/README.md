# E-Commerce SaaS Monorepo (Flask)

A full-stack e-commerce application built as a **single monorepo** with a **microservices-style folder layout**.

## What is included
- Flask backend with modular blueprints
- Service-separated folders:
  - `auth_service/`
  - `product_service/`
  - `cart_service/`
  - `order_service/`
  - `payment_service/`
  - `user_service/`
  - `admin_service/`
  - `notification_service/`
- SQLAlchemy ORM
- JWT-based API authentication
- Environment-based config
- Error handling and structured logging
- Premium dark UI using Flask + Jinja + Bootstrap 5 + Alpine.js
- Admin dashboard with KPIs, product/order/user/content management
- Sample seed script and database schema
- OpenAPI / Swagger-style documentation

## Tech Stack
- Python 3.11+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- Flask-Bcrypt
- Flask-CORS
- Bootstrap 5
- Chart.js
- Alpine.js

## Project Layout
```
backend/
  app.py
  wsgi.py
  config.py
  requirements.txt
  .env.example
  api_docs/openapi.yaml
  database/schema.sql
  migrations/
  shared/
  auth_service/
  product_service/
  cart_service/
  order_service/
  payment_service/
  user_service/
  admin_service/
  notification_service/
  templates/
  static/
```

## Quick Start

### 1) Create a virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Configure environment
Copy `.env.example` to `.env` and update values.

### 4) Initialize database
Default config uses SQLite for convenience.
For PostgreSQL or MySQL, set `DATABASE_URL`.

Run the commands from the repository root.

```bash
flask --app app db init
flask --app app db migrate -m "initial"
flask --app app db upgrade
```

### 5) Seed sample data
```bash
python seed.py
```

### 6) Run the app
```bash
python app.py
```

Open:
- Storefront: `http://127.0.0.1:5000/`
- Admin login: `http://127.0.0.1:5000/admin/login`
- API docs: use `api_docs/openapi.yaml`

## Default Demo Accounts
Seed script creates:
- Admin: `admin@demo.com` / `Admin@123`
- User: `user@demo.com` / `User@123`

## Notes
- "Payment" is implemented as a mock payment flow so the app is safe for local demo use.
- JWT endpoints are included for API consumption.
- Storefront pages use session-based login for a smoother browser experience, while REST endpoints support JWT.

## Project is made under AasmaX 

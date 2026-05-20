# Distributed Order Management System (Backend)

A robust, highly scalable, microservices-inspired backend system for managing orders, inventory, and asynchronous payments. Built with Django REST Framework, Celery, Redis, and MySQL.

## 🏗 Architecture & Design Decisions

### 1. Modular Monolith ("Microservices-Inspired")
Instead of deploying 4 separate physical servers (which adds massive DevOps overhead for a system of this size), I used a **Modular Monolith** pattern.
* The system runs as a single API Gateway (Django).
* Internally, domains are strictly decoupled into independent apps (`users`, `inventory`, `orders`, `payments`).
* Cross-domain communication (like Orders -> Payments) is handled asynchronously via **Celery & Redis** to prevent blocking HTTP requests.

### 2. Database Design & Integrity
* **UUID Primary Keys:** All tables use UUIDs instead of auto-incrementing integers. This prevents ID enumeration attacks and completely avoids ID collisions in distributed database scenarios.
* **ACID Transactions & Row-Level Locking:** When placing an order, I use `transaction.atomic()` and `select_for_update()`. This locks the specific product row in MySQL to prevent **race conditions** if two users attempt to buy the last item at the exact same millisecond.
* **Historical Integrity:** The `OrderItem` model copies the `price_at_time` from the Product. If an Admin changes a product price tomorrow, historical invoices remain 100% accurate. 

### 3. Asynchronous Workflow (Celery + Redis)
To prevent the user from waiting for a slow payment gateway response:
1. Order is validated, stock is reserved, and Order is saved as `INVENTORY_RESERVED`.
2. A Celery task `process_payment.delay(order_id)` is pushed to the Redis message broker.
3. The API immediately returns a `201 Created` response to the React Frontend.
4. The background Celery worker picks up the task, simulates a payment gateway delay, and updates the Order status to `COMPLETED` or `PAYMENT_FAILED`.
5. If the payment fails, the Celery task safely rolls back the reserved inventory stock.

## 🔐 Authentication & Security Flow

* **JWT (JSON Web Tokens):** Used for stateless, scalable authentication. Tokens expire after 60 minutes, with refresh tokens lasting 1 day.
* **Role-Based Access Control (RBAC):** Custom permission classes (`IsAdminRole`, `IsCustomerRole`) strictly protect endpoints. Customers cannot access Admin routes.
* **Logout Blacklisting:** `POST /api/auth/logout/` blacklists the submitted refresh token, while the frontend immediately removes stored access and refresh tokens.
* **Global Exception Handling:** A centralized Exception Handler catches all errors and formats them into a strict standard JSON response, ensuring internal stack traces never leak to the client.

## 🚀 Setup Instructions

### Prerequisites
* Python 3.11+
* MySQL Server
* Redis Server (Native Windows port or WSL)

### 1. Database & Environment
1. Start your local MySQL server and create an empty database: `CREATE DATABASE order_management;`
2. Clone this repository and navigate to the `backend` folder.
3. Rename `.env.example` to `.env` and fill in your local MySQL credentials.

### 2. Install Dependencies
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Migrations & Superuser
```bash
python manage.py makemigrations
python manage.py migrate

# Create an Admin user (optional but recommended)
python manage.py createsuperuser
```

### 4. Running the Application
You will need **two** terminal windows running simultaneously.

**Terminal 1 (Django API Server):**
```bash
python manage.py runserver
```
*API will be available at http://127.0.0.1:8000*
*Swagger Docs available at http://127.0.0.1:8000/swagger/*

**Terminal 2 (Celery Background Worker):**
```bash
# Windows users must use the 'solo' pool for Celery
celery -A config worker --loglevel=info --pool=solo
```

## 🧾 Audit Logging
* The backend includes an `AuditLog` model and `AuditMiddleware`.
* Every `/api/` request is recorded with `user`, `method`, `path`, `IP address`, `status code`, and request payload.
* Sensitive fields such as `password` are sanitized before logging.

## Admin User Management
Admins can manage users through protected `/api/users/` endpoints:
* `GET /api/users/` lists users.
* `POST /api/users/` creates customer or admin accounts.
* `PATCH /api/users/{id}/` updates profile fields, role, active state, or password.
* `DELETE /api/users/{id}/` deletes users, with self-delete blocked.

Public registration always creates `CUSTOMER` users. Admin roles can only be assigned from the authenticated admin user-management API.

## 🔁 Celery Retry & Payment Reliability
* Celery payment tasks now include retry support with `max_retries=3` and a `30s` default retry delay.
* If the payment worker encounters a transient failure, the task automatically retries instead of silently failing.
* The order lifecycle is preserved: reserved inventory may be restored safely if payment ultimately fails.

## 🧪 Testing the Backend
Run the test suite with `pytest` from the `backend` folder:
```bash
cd backend
pytest
```

Generate a coverage report for the Django apps:
```bash
pytest --cov=. --cov-report=term-missing
```

If you want to run a specific app test file:
```bash
pytest apps/orders/tests.py
```

## 📝 Logs and Diagnostics
* **API logs:** Django request/response logs appear in the `python manage.py runserver` terminal.
* **Celery logs:** Background task processing logs appear in the Celery terminal when running:
  ```bash
  celery -A config worker --loglevel=info --pool=solo
  ```
* **Audit logs:** Request audit events are persisted using the `AuditLog` model. You can inspect them via Django Admin or the Django shell:
  ```bash
  python manage.py shell
  >>> from common.models import AuditLog
  >>> AuditLog.objects.all().count()
  ```

## ⚖️ Tradeoff Discussions
* **MySQL vs PostgreSQL:** MySQL was chosen based on hardware constraints and environment. Both support ACID transactions perfectly for this use case.
* **Modular Monolith vs Physical Microservices:** Given the memory constraints (8GB RAM) and the overhead of Docker/Kubernetes, a physical microservice architecture would fail to run locally. The Modular Monolith offers the exact same logical separation of concerns but runs extremely fast and lightweight.
* **Soft Deletes:** Currently, Products are "soft-deleted" using `is_active=False` rather than hard deleted to preserve Order history. This increases DB size over time but is a mandatory tradeoff for compliance.

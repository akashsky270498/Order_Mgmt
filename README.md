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

### Swagger Documentation
Interactive API documentation is available at:
```
http://127.0.0.1:8000/swagger/
```
Try all endpoints directly from your browser with auto-generated forms.

### Postman Collection
A complete Postman collection is included in this repository: `Postman_Collection.json`

**To import in Postman:**
1. Open Postman
2. Click **Import** → **Upload Files**
3. Select `Postman_Collection.json`
4. Set the environment variables (access_token, admin_token, user_id, etc.) after logging in

**Collection includes:**
- ✅ Authentication (register, login, logout, refresh)
- ✅ User Management (list, toggle status, profile, password)
- ✅ Product Management (CRUD)
- ✅ Order Management (create, list, update, cancel)
- ✅ Payment Tracking
- ✅ Admin Analytics

### Pytest Unit Tests
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

### Architecture & Technology Choices
* **MySQL vs PostgreSQL:** MySQL was chosen based on hardware constraints and environment. Both support ACID transactions perfectly for this use case.
* **Modular Monolith vs Physical Microservices:** Given the memory constraints (8GB RAM) and the overhead of Docker/Kubernetes, a physical microservice architecture would fail to run locally. The Modular Monolith offers the exact same logical separation of concerns but runs extremely fast and lightweight.
* **Soft Deletes:** Currently, Products are "soft-deleted" using `is_active=False` rather than hard deleted to preserve Order history. This increases DB size over time but is a mandatory tradeoff for compliance.

### Deployment & Infrastructure

#### Docker Not Implemented
- **Reason:** The development system has only 8GB of RAM. Docker adds significant memory overhead for container runtime, images, and services. Running Docker locally caused the system to hang and become unresponsive, making development extremely slow and frustrating.
- **Trade-off:** Development is faster and more responsive on the host machine. For production deployment, Docker would provide excellent benefits (consistency, scaling, CI/CD). However, for local development and this assessment timeline, running natively was the pragmatic choice.
- **For Production:** Dockerfile and docker-compose.yml can be easily created following standard Django best practices if needed for cloud deployment.

#### Backend & Frontend Not Hosted
- **Reason:** The database hosting attempted on Railway.com failed due to URL/connection configuration issues (likely MySQL/connection pool settings not properly configured for the Railway environment).
- **Trade-off:** Without a reliable hosted database, hosting the backend and frontend separately would create deployment fragmentation and testing complexity. Testing requires backend + frontend + database to work together seamlessly.
- **Current Status:** The complete application can be tested locally by following the Setup Instructions above. Both GitHub repositories contain full, working code with Swagger API documentation.

### How to Test the Application
Since the application is not currently hosted, follow these steps to test locally:

1. **Backend Setup** (this repository):
   ```bash
   cd backend
   .\venv\Scripts\activate
   python manage.py migrate
   python manage.py runserver
   ```
   Access Swagger docs at `http://127.0.0.1:8000/swagger/`

2. **Celery Worker** (in a separate terminal):
   ```bash
   cd backend
   .\venv\Scripts\activate
   celery -A config worker --loglevel=info --pool=solo
   ```

3. **Frontend Setup** (separate repository):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Access the application at `http://127.0.0.1:5173/`

4. **API Testing:** Use the Swagger interface at `http://127.0.0.1:8000/swagger/` or the Postman collection provided in the GitHub repository. 

# Centralized License Service (group.one)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python version](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Django version](https://img.shields.io/badge/Django-5.2-green)](https://www.djangoproject.com/)
[![CI Status](https://github.com/Chibueze-Adeyemi-Ajayi/group_one_assessment/actions/workflows/ci.yml/badge.svg)](https://github.com/Chibueze-Adeyemi-Ajayi/group_one_assessment/actions)

A high-performance, multi-tenant License Service designed to act as the single source of truth for licenses and entitlements across various brands (WP Rocket, Imagify, RankMath, etc.) within the **group.one** ecosystem.

## 🚀 Overview
This service provides a centralized authority for the license lifecycle:
- **For Brands**: Provision, renew, suspend, and query licenses via secure internal APIs.
- **For Products**: Activate, validate, and manage seat allocations for end-user applications (plugins, apps, CLIs).

## 🛠 Tech Stack
- **Framework**: Django REST Framework (DRF)
- **Database**: PostgreSQL (Production) / SQLite3 (Development)
- **Auth**: SimpleJWT (JSON Web Tokens)
- **Documentation**: Swagger UI / drf-spectacular
- **Configuration**: Django-environ (dotenv)

## ✨ Features (Implemented)
- **US1: Brand Provisioning**: Create license keys and multi-product licenses.
- **US3: Activation System**: Domain-based or machine-id based license activation.
- **US4: Validation**: Product-facing APIs to check status and remaining seats.
- **US6: Admin Discovery**: List all customer licenses across the ecosystem (Admin/Brand only).
- **Multi-Tenancy**: Strategic separation of data between brands (Brand A cannot manage Brand B's licenses).

## 📖 Documentation
Detailed architectural decisions, data models, and trade-offs are documented in [EXPLANATION.md](./EXPLANATION.md).

### API Reference
Once the server is running, you can access interactive documentation:
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **Redoc**: `http://localhost:8000/api/redoc/`

### 📮 Postman Collection
A pre-configured Postman collection is available in the root directory: `Centralized_License_Service.postman_collection.json`.

**How to Import:**
1. Open Postman and click **Import**.
2. Drag and drop the `.json` file.
3. The collection is pre-set with a `base_url` variable and includes a **Post-login script** that automatically saves your JWT token for subsequent requests.

---

## ⚙️ Local Setup

### 1. Prerequisites
- Python 3.10+
- PostgreSQL (optional, defaults to SQLite)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Chibueze-Adeyemi-Ajayi/group_one_assessment.git
cd group_one_assessment/group_one

# Create a virtual environment
python -m venv venv
source venv/bin/Scripts/activate  # Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the `group_one/` directory. You can either use a full connection string or individual components (preferred for Docker):

```env
DEBUG=True
SECRET_KEY=your-secret-key-change-this

# Option A: Individual components (Recommended for Docker Compose)
DB_NAME=group_one_db
DB_USER=postgres
DB_PASSWORD=postgres

# Option B: Full Connection String (Standard Django)
# DATABASE_URL=postgres://user:password@localhost:5432/group_one_db
```

### 4. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser  # Recommended for admin access
```

### 5. Running the API
```bash
python manage.py runserver
```

### 🐳 Running with Docker Compose (Recommended)
This will set up the API and a PostgreSQL database automatically:
```bash
docker-compose up --build
```

---

## 🧪 Testing
Run the automated test suite to verify the logic (auth, seat limits, multi-tenancy):
```bash
python manage.py test api
```

## 🏗 Continuous Integration (CI)
This project uses **GitHub Actions** for CI. On every push and pull request, the workflow:
1.  Spins up a **PostgreSQL 15** service.
2.  Installs all Python dependencies.
3.  Runs database migrations.
4.  Executes the automated test suite.

The configuration can be found in `.github/workflows/ci.yml`.

---

## 🔬 Observability & Performance
- **Logging**: The application uses structured logging to track provisioning and activation events.
- **Caching**: License status checks (`/api/status/`) are cached in-memory for 1 hour to ensure high performance under load.

## 🧪 Quick Test (Sample Request)
Obtain a JWT token to authenticate as a Brand administrator:
```bash
curl -X POST http://localhost:8000/api/auth/token/ \\
     -H "Content-Type: application/json" \\
     -d '{"username": "your_admin", "password": "your_password"}'
```

---

## 📂 Project Structure
- `assessment/`: Project configuration and core settings.
- `api/`: The primary app containing models, views, and serializers for the License Service.
- `.env`: Local environment variables.
- `requirements.txt`: Python package dependencies.

---

## ☕ Support
For questions or clarifications regarding this implementation, please contact **Jilo developer**.

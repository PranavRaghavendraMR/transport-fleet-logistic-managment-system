# TRANSPORT FLEET & LOGISTICS MANAGEMENT SYSTEM (FMS)
## Vercel Cloud Serverless Deployment & Architecture Guide

**Student Name:** Pranavraghavendra M R  
**Registration Number:** 24UG00220  
**Institution:** Chanakya University, School of Engineering  
**Department:** Computer Applications & Technology  
**Program:** Bachelor of Computer Applications (BCA V Semester)  
**Course Code:** DAT501 – Full Stack Development  
**GitHub Repository:** [https://github.com/PranavRaghavendraMR/transport-fleet-logistic-managment-system.git](https://github.com/PranavRaghavendraMR/transport-fleet-logistic-managment-system.git)  
**Target Vercel Team:** Pranav  
**Target Project Name:** `transport-fleet-logistics-management-system`  

---

## 1. Executive Deployment Summary

The **Transport Fleet & Logistics Management System (FMS)** has been engineered for production deployment on **Vercel's Serverless Platform** using Python serverless runtime, Django WSGI, WhiteNoise static file compression, and persistent PostgreSQL cloud database support.

### Production Architecture
```
                                 [ Web Clients / Mobile Browsers ]
                                                │
                                                ▼ (HTTPS / TLS 1.3)
                                ┌────────────────────────────────┐
                                │      Vercel Edge Network       │
                                │   (Global CDN & Anycast DNS)   │
                                └───────┬────────────────┬───────┘
                                        │                │
                        ┌───────────────┘                └──────────────┐
                        ▼                                               ▼
          [ Static Assets CDN ]                               [ Serverless Python Runtime ]
         • /static/* -> WhiteNoise                           • WSGI Callable: api/index.py
         • Pre-compressed & hashed                           • Django 5.2 (Python 3.11)
         • Gzip & Brotli encoding                            • Ephemeral Lambda Containers
                                                                        │
                                                                        ▼ (Encrypted Connection Pool)
                                                              ┌───────────────────────────┐
                                                              │   Cloud PostgreSQL DB     │
                                                              │   (Neon / Supabase / GCP) │
                                                              │   via DATABASE_URL        │
                                                              └───────────────────────────┘
```

---

## 2. Serverless Runtime & File Structure

Unlike conventional long-running VPS servers (e.g. EC2/GCE) running Nginx + Gunicorn, Vercel executes Django requests in ephemeral serverless lambdas.

### Directory Configuration
```
d:\pranav\transport-fms\
├── api/
│   └── index.py               # WSGI Entry Point for Vercel Serverless Function
├── transport_fms/
│   ├── settings.py            # Environment-aware production Django settings
│   ├── urls.py                # Global URL routing
│   ├── wsgi.py                # Standalone WSGI application
│   └── asgi.py                # Standalone ASGI application
├── fleet/                     # Module 1: Fleet Operations & Drivers
├── routing/                   # Module 1: Transportation Routes & Dispatch
├── maintenance/               # Module 2: Workshop Maintenance & Servicing
├── safety/                    # Module 3: Safety Incidents & Inspections
├── fuel/                      # Module 4: Fuel Logs, Mileage & Expenses
├── accounts/                  # Multi-Role RBAC & Authentication
├── reports/                   # 9 Comprehensive Analytical Reports
├── templates/                 # 28 Jinja/Django Responsive Templates
├── static/                    # Custom CSS & JavaScript assets
├── staticfiles/               # Pre-collected, hashed, WhiteNoise-ready assets
├── vercel.json                # Vercel Deployment Specification
├── build_files.sh             # Vercel Build Pipeline Script
├── requirements.txt           # Production Python dependencies
├── .env.example               # Template for environment variables
└── manage.py                  # Django Management Utility
```

---

## 3. Deployment Configuration Files

### 3.1 `api/index.py` (Serverless WSGI Entry Point)
```python
import os
import sys
from pathlib import Path

# Add project root directory to sys.path so modules resolve cleanly
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_fms.settings')

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
```

### 3.2 `vercel.json` (Deployment Specification)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb",
        "runtime": "python3.11"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "DJANGO_SETTINGS_MODULE": "transport_fms.settings"
  }
}
```

### 3.3 `requirements.txt` (Production Dependencies)
```
Django>=5.0,<6.0
asgiref>=3.8.1
sqlparse>=0.5.0
whitenoise>=6.6.0
dj-database-url>=2.1.0
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0
```

---

## 4. Production Database Configuration

### PostgreSQL Support
Vercel serverless containers are ephemeral; local SQLite databases cannot persist database writes across serverless invocations. Therefore, `transport_fms/settings.py` includes dynamic database resolution via `dj-database-url`:

```python
import os
import dj_database_url

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

### Supported PostgreSQL Providers
The project connects out of the box to any PostgreSQL service by setting the `DATABASE_URL` environment variable:
- **Neon Serverless Postgres:** `postgres://user:password@ep-xyz.region.aws.neon.tech/neondb?sslmode=require`
- **Supabase Postgres:** `postgres://postgres.xxx:password@aws-0-region.pooler.supabase.com:6543/postgres`
- **Google Cloud SQL / AlloyDB:** `postgres://user:password@host:5432/dbname`
- **Render / Railway / Aiven Postgres:** standard connection string format.

---

## 5. Environment Variables for Vercel

Configure these in the Vercel Dashboard (**Project Settings -> Environment Variables**) or via Vercel CLI:

| Variable | Recommended Production Value | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | *(Strong 50+ character random string)* | Cryptographic signing key |
| `DEBUG` | `False` | Disables debug mode in production |
| `DATABASE_URL` | `postgresql://user:pass@host:5432/dbname?sslmode=require` | Persistent cloud database |
| `ALLOWED_HOSTS` | `*.vercel.app,localhost,127.0.0.1` | Permitted hostnames |
| `CSRF_TRUSTED_ORIGINS` | `https://*.vercel.app` | Prevents CSRF rejection on Vercel subdomains |
| `PYTHON_VERSION` | `3.11` | Serverless Python runtime version |

---

## 6. Static File Management (WhiteNoise)

Static files (Bootstrap 5, Chart.js, Bootstrap Icons, custom CSS/JS) are managed through **WhiteNoise**:
- `STATIC_ROOT`: `BASE_DIR / 'staticfiles'`
- Storage Backend: `'whitenoise.storage.CompressedManifestStaticFilesStorage'`
- All 129 static assets have been pre-collected and 387 hash-versioned assets generated for instant caching and zero runtime latency.

---

## 7. Step-by-Step Vercel Deployment Commands

### Option A: Via GitHub Integration (Recommended)
1. Go to [https://vercel.com/new](https://vercel.com/new) logged in as **Pranav**.
2. Select repository: `PranavRaghavendraMR/transport-fleet-logistic-managment-system`.
3. In Project Configuration:
   - **Framework Preset:** Other
   - **Root Directory:** `./`
   - **Build Command:** `bash build_files.sh` (or leave default)
   - **Output Directory:** `staticfiles`
4. Add Environment Variables:
   - `SECRET_KEY`: `<your-production-secret-key>`
   - `DEBUG`: `False`
   - `DATABASE_URL`: `<your-postgresql-url>`
5. Click **Deploy**.

### Option B: Via Vercel CLI
```bash
# 1. Log in to Vercel
vercel login

# 2. Link to Project in team Pranav
vercel link --scope Pranav --yes

# 3. Set Environment Variables
vercel env add SECRET_KEY production
vercel env add DATABASE_URL production
vercel env add DEBUG production

# 4. Deploy to Production
vercel --prod
```

### Option C: Database Migration & Seeding on PostgreSQL
Once connected to the cloud PostgreSQL database:
```bash
python manage.py migrate
python manage.py seed_data
```

---

## 8. Verification Evidence

### Automated Test Suite: 18/18 Tests Passed (100%)
```text
Ran 18 tests in 60.323s
OK
```

### Full Live HTTP Audit: 37/37 Endpoints Passed
- **Executive Dashboard:** HTTP 200
- **Fleet Management (Vehicles & Drivers):** HTTP 200
- **Transportation Routing & Dispatch:** HTTP 200
- **Workshop Maintenance & Work Orders:** HTTP 200
- **Safety Incidents & Road Inspections:** HTTP 200
- **Fuel Logs, Mileage & Consumption:** HTTP 200
- **All 9 Analytical Reports:** HTTP 200
- **Role-Based Access Control (RBAC):** HTTP 302 safe redirection enforced for all unauthenticated and unauthorized requests.

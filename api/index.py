"""
Vercel Serverless WSGI Handler for Transport Fleet & Logistics Management System (FMS).
Chanakya University - School of Engineering - BCA V Sem (DAT501)
Student: Pranavraghavendra M R (Reg No: 24UG00220)
"""
import os
import sys
import shutil
from pathlib import Path

# Add project root directory to sys.path so apps and settings resolve cleanly
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Pre-initialize writable SQLite database in /tmp for Vercel serverless environment
source_db = PROJECT_ROOT / 'db.sqlite3'
tmp_db = Path('/tmp') / 'db.sqlite3'
if source_db.exists():
    try:
        Path('/tmp').mkdir(parents=True, exist_ok=True)
        if not tmp_db.exists() or tmp_db.stat().st_size == 0:
            shutil.copy2(source_db, tmp_db)
    except Exception:
        pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_fms.settings')

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()

"""
Vercel Serverless WSGI Handler for Transport Fleet & Logistics Management System (FMS).
Chanakya University - School of Engineering - BCA V Sem (DAT501)
Student: Pranavraghavendra M R (Reg No: 24UG00220)
"""
import os
import sys
from pathlib import Path

# Add project root directory to sys.path so apps and settings resolve cleanly
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_fms.settings')

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()

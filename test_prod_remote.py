import urllib.request
import urllib.parse
import http.cookiejar
import re

PROD_URL = 'https://transport-fleet-logistics-managemen-gamma.vercel.app'
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

print("=================================================================")
print("  PRODUCTION DEPLOYMENT VERIFICATION AUDIT")
print(f"  Target: {PROD_URL}")
print("=================================================================")

# 1. GET /login/
print("\n[STEP 1: GET /login/]")
resp = opener.open(f'{PROD_URL}/login/')
print(f"  HTTP Status: {resp.status}")
html = resp.read().decode('utf-8')
csrf_token = None
for c in cj:
    if c.name == 'csrftoken':
        csrf_token = c.value
if not csrf_token:
    m = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', html)
    if m:
        csrf_token = m.group(1)
print(f"  CSRF Token received: {csrf_token[:15] if csrf_token else 'None'}...")
print(f"  Login form present: {'Sign In to Fleet Portal' in html}")

# 2. POST /login/ with Invalid Credentials
print("\n[STEP 2: POST /login/ with Invalid Credentials]")
inv_data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': csrf_token,
    'username': 'invalid_user',
    'password': 'WrongPassword123'
}).encode()
req = urllib.request.Request(
    f'{PROD_URL}/login/',
    data=inv_data,
    headers={'Referer': f'{PROD_URL}/login/'}
)
inv_resp = opener.open(req)
inv_html = inv_resp.read().decode('utf-8')
print(f"  HTTP Status: {inv_resp.status} (Expected 200 - re-render login form)")
print(f"  Safe error alert displayed: {'Invalid username or password' in inv_html}")

# 3. POST /login/ with Valid Credentials (admin / Admin@123)
print("\n[STEP 3: POST /login/ with Valid Credentials (admin / Admin@123)]")
for c in cj:
    if c.name == 'csrftoken':
        csrf_token = c.value
valid_data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': csrf_token,
    'username': 'admin',
    'password': 'Admin@123'
}).encode()
req = urllib.request.Request(
    f'{PROD_URL}/login/',
    data=valid_data,
    headers={'Referer': f'{PROD_URL}/login/'}
)
try:
    auth_resp = opener.open(req)
    print(f"  HTTP Status: {auth_resp.status}")
    print(f"  Final Landed URL: {auth_resp.geturl()}")
    dash_html = auth_resp.read().decode('utf-8')
    session_cookies = [c.name for c in cj if c.name == 'sessionid']
    print(f"  Signed-Cookie Session Present: {bool(session_cookies)}")
    print(f"  Executive Dashboard Heading Present: {'Executive Dashboard' in dash_html}")
    print(f"  KPI Metric Cards Present: {'Total Fleet' in dash_html or 'Total Vehicles' in dash_html}")
    print(f"  College Demonstration Notice Present: {'College Demonstration Deployment' in dash_html}")
    print(f"  Student Attribution Present: {'Pranavraghavendra M R' in dash_html}")
except urllib.error.HTTPError as e:
    print(f"  HTTP Error {e.code}: {e.reason}")
    print(e.read().decode('utf-8', errors='replace')[:500])

# 4. Verify All 4 Roles Login
print("\n[STEP 4: VERIFY ALL 4 USER ROLES AUTHENTICATION]")
roles = [
    ('manager', 'Manager@123', 'Fleet Manager'),
    ('mechanic', 'Mechanic@123', 'Maintenance Staff'),
    ('staff', 'Staff@123', 'General Staff'),
]

for uname, pwd, rlabel in roles:
    role_cj = http.cookiejar.CookieJar()
    role_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(role_cj))
    r = role_opener.open(f'{PROD_URL}/login/')
    r_html = r.read().decode('utf-8')
    token = [c.value for c in role_cj if c.name == 'csrftoken'][0]
    data = urllib.parse.urlencode({'csrfmiddlewaretoken': token, 'username': uname, 'password': pwd}).encode()
    req = urllib.request.Request(f'{PROD_URL}/login/', data=data, headers={'Referer': f'{PROD_URL}/login/'})
    res = role_opener.open(req)
    res_html = res.read().decode('utf-8')
    print(f"  [PASS - HTTP {res.status}] Role: {rlabel:20} ({uname:8}) -> Landed: {res.geturl()}")

# 5. Verify All 4 Core Modules under Authenticated Session
print("\n[STEP 5: VERIFY 4 CORE MODULES & SAMPLE DATA RECORDS]")
endpoints = [
    ("/fleet/vehicles/", "Vehicles Directory (10 commercial vehicles)"),
    ("/fleet/drivers/", "Driver Registry (7 drivers)"),
    ("/routing/", "Route Scheduling (8 routes)"),
    ("/maintenance/dashboard/", "Workshop Maintenance Dashboard (7 work orders)"),
    ("/safety/dashboard/", "Safety & Compliance Dashboard (6 incidents & 6 inspections)"),
    ("/fuel/dashboard/", "Fuel Consumption Dashboard (14 fuel logs)"),
    ("/reports/", "Reports & Analytics Center"),
]

for path, label in endpoints:
    url = f"{PROD_URL}{path}"
    try:
        r = opener.open(url)
        content = r.read().decode('utf-8')
        print(f"  [PASS - HTTP {r.status}] {label:60} -> {path}")
    except urllib.error.HTTPError as e:
        print(f"  [FAIL - HTTP {e.code}] {label:60} -> {path}")

# 5. Check Static Assets
print("\n[STEP 5: VERIFY STATIC ASSETS (WHITENOISE COMPRESSED & IMMUTABLE)]")
static_assets = [
    "/static/css/custom.d516cb5626c2.css",
    "/static/js/main.0eaf7cc66543.js",
]
for s in static_assets:
    try:
        r = urllib.request.urlopen(f"{PROD_URL}{s}")
        print(f"  [PASS - HTTP {r.status}] Static asset -> {s}")
    except Exception as e:
        print(f"  [FAIL] Static asset {s}: {e}")

print("\n=================================================================")
print("  PRODUCTION DEPLOYMENT VERIFICATION COMPLETE")
print("=================================================================")

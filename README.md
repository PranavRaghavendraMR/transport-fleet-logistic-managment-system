# Transport Fleet & Logistics Management System (FMS)

**A Centralized Commercial Transport Fleet, Routing, Maintenance, Safety, and Fuel Logistics Platform**

- **Student Name:** Pranavraghavendra M R  
- **Registration Number:** 24UG00220  
- **University:** Chanakya University  
- **Department:** School of Engineering  
- **Course:** Bachelor of Computer Applications (BCA) - V Semester  
- **Subject:** Full Stack Development (DAT501)  
- **Technology:** Django Full Stack Web Architecture  

---

## 1. Project Overview & Problem Statement

Commercial road freight and logistics transport companies face critical operational challenges managing distributed fleets of heavy trucks, line-haul carriers, delivery vans, and intra-city cargo vehicles. Common operational bottlenecks include:

1. **Unplanned Downtime & Overdue Servicing:** Lack of real-time workshop tracking leads to missed preventive maintenance and unexpected en-route breakdowns.
2. **Double-Booking & Route Conflicts:** Disconnected dispatchers inadvertently assign vehicles or drivers already in transit or held under workshop repair.
3. **Regulatory Non-Compliance:** Unmonitored vehicle insurance or commercial driver driving licence expiry dates lead to punitive police challans, vehicle impoundment, and insurance repudiation.
4. **Opaque Fuel Costs & Mileage Leakage:** Fuel purchases are recorded loosely on paper receipts without mathematical verification of fuel mileage ($\text{km/L}$) derived from consecutive odometer readings.
5. **Safety Incident Blindspots:** Lack of a centralized audit trail for road accidents, damage severity, and roadworthiness inspections.

The **Transport Fleet & Logistics Management System (FMS)** resolves these challenges by providing a centralized, role-authenticated enterprise web portal that unifies vehicle inventory, driver rosters, transit route scheduling, workshop maintenance work orders, safety compliance, and fuel consumption telemetry.

---

## 2. Technology Stack

- **Backend:** Python 3.11 & Django 5.2
- **Frontend:** HTML5, CSS3, JavaScript (ES6)
- **UI Framework:** Bootstrap 5.3 & Bootstrap Icons 1.11
- **Database:** SQLite 3 (Django ORM with ForeignKey relationships, unique constraints, and transaction integrity)
- **Template Engine:** Django Template Language (DTL) with template inheritance and custom context processors
- **Data Visualizations:** Chart.js 4.4 (interactive doughnuts, monthly bar charts, and efficiency rankings)
- **Authentication & RBAC:** Django Authentication System with `UserProfile` model and custom decorators (`@admin_required`, `@fleet_manager_required`, `@maintenance_staff_required`)

---

## 3. Core Functional Modules

### Module 1: Fleet Operations & Routing
- **Vehicle Directory:** Full CRUD operations for commercial vehicles (Trucks, Vans, Buses, Mini Trucks). Tracks registration number, make, model, capacity ($\text{kg}$), fuel type, odometer, insurance, and road status (`Available`, `In Use`, `Maintenance`).
- **Driver Management:** Driver records, contact numbers, unique driving licence numbers, licence expiry alerts, and employment status (`Active`, `On Leave`, `Suspended`, `Terminated`).
- **Transportation Route Dispatch:** Origin, destination, distance ($\text{km}$), estimated duration, cargo description, vehicle assignment, and driver assignment.
- **Assignment Validation:** Pre-save validation prevents assigning vehicles in `Maintenance` or drivers whose licences are expired or who are already assigned to active trips. Automatically shifts vehicle status to `In Use` during transit, and restores `Available` upon completion.

### Module 2: Workshop Maintenance
- **Service Work Orders:** Preventive servicing, engine repairs, brake overhauls, tyre replacements, and electrical repairs.
- **Cost Computation:** Automatically computes $\text{Total Maintenance Cost} = \text{Spare Parts Cost} + \text{Labour Cost}$.
- **Automatic Status Synchronization:** Scheduling or starting work orders shifts vehicle status to `Maintenance`. Marking work completed restores vehicle status to `Available`.
- **Preventive Maintenance Reminders:** Visual overdue alerts for vehicles exceeding scheduled maintenance deadlines.

### Module 3: Safety Management & Compliance
- **Incident Audit Trail:** Captures incident ID, vehicle, driver, date, highway location, category (Collision, Scrape, Breakdown, Overspeeding), damage severity (`Low`, `Medium`, `High`, `Critical`), estimated repair cost, and actions taken.
- **Roadworthiness Inspections:** Standardized multi-point audits (brakes, tyres, lights, on-board documents) with verdicts (`Passed`, `Conditional Pass`, `Failed`).
- **Compliance Watchlist:** Live 30-day lookahead alerts for expiring vehicle insurance policies and driver licences.

### Module 4: Fuel Management & Telemetry
- **Fuel Purchase Records:** Vehicle, fuel type (Diesel, Petrol, CNG, Electric), quantity ($\text{L}$), unit price, fueling vendor, and invoice number.
- **Total Cost Formula:** $\text{Total Fuel Cost} = \text{Quantity (L)} \times \text{Price per Litre (₹)}$.
- **Mathematical Mileage Formula:** $\text{Mileage (km/L)} = \frac{\text{Current Odometer} - \text{Previous Odometer}}{\text{Fuel Quantity}}$.
- **Auditing Methodology:** Automatically pairs consecutive refuel logs for each vehicle to calculate distance run and consumption rate.

### Module 5: Executive Dashboard & Reports
- **10 Executive KPI Cards:** Total Vehicles, Available Vehicles, In Use, Maintenance, Total Drivers, Active Routes, Pending Maintenance, Total Fuel Expenses, Total Maintenance Costs, and Open Incidents.
- **Interactive Visualizations:** Fleet availability distribution doughnut, monthly operational expense trends (fuel vs maintenance), and mileage performance bars.
- **9 Filterable & Printable Reports:** Vehicle Inventory, Vehicle Availability, Driver Compliance, Route Performance, Maintenance History, Maintenance Expenses, Safety Incidents, Fuel Expenses, and Vehicle Mileage.

---

## 4. User Roles and Security Permissions

| Role | Vehicle / Driver CRUD | Route Dispatch | Workshop Logging | Fuel Purchases | Safety Filing | Access Control |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Administrator** (`admin`) | Full Access | Full Access | Full Access | Full Access | Full Access | Full Access |
| **Fleet Manager** (`manager`) | Full Access | Full Access | View Only | Full Access | Full Access | View Only |
| **Maintenance Staff** (`mechanic`) | View Only | View Only | Full Access | View Only | View Only | Denied |
| **General Staff** (`staff`) | View Only | View Only | View Only | Create Allowed | Create Allowed | Denied |

---

## 5. Demonstration Credentials

The seed command populates realistic Indian transportation demonstration accounts:

| Role | Username | Password | Email | Full Name |
|---|---|---|---|---|
| **Administrator** | `admin` | `Admin@123` | `admin@transportfms.edu` | Pranavraghavendra M R |
| **Fleet Manager** | `manager` | `Manager@123` | `manager@transportfms.edu` | Rajesh Kumar |
| **Maintenance Staff** | `mechanic` | `Mechanic@123` | `mechanic@transportfms.edu` | Suresh Babu |
| **General Staff** | `staff` | `Staff@123` | `staff@transportfms.edu` | Ananya Sharma |

---

## 6. Installation & Execution Guide

### Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Git (optional)

### Setup Instructions

1. **Navigate to the Project Directory:**
   ```bash
   cd d:\pranav\transport-fms
   ```

2. **Install Required Packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply Database Migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Seed Demonstration Data (Indian Fleet, Drivers, Routes, Fuel, Maintenance):**
   ```bash
   python manage.py seed_data
   ```

5. **Start Development Server:**
   ```bash
   python manage.py runserver
   ```
   *Or double click `run.bat` on Windows.*

6. **Access Application:**
   Open browser at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 7. Automated Testing

Run the automated test suite covering all 18 functional validation scenarios:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

Run the end-to-end live integration script:
```bash
python test_live_system.py
```

---

## 8. Cloud Serverless & Vercel Deployment

The project is fully configured for deployment on **Vercel** with Python serverless functions, WhiteNoise static asset serving, and cloud PostgreSQL integration.

### Deployment Files
- `api/index.py`: Serverless WSGI entry point
- `vercel.json`: Deployment routes and python runtime configuration
- `build_files.sh`: Automated dependency installation and `collectstatic` script
- `DEPLOYMENT.md`: Comprehensive cloud architecture and environment setup guide

For complete step-by-step cloud deployment instructions, see [DEPLOYMENT.md](file:///d:/pranav/transport-fms/DEPLOYMENT.md).

---

## 9. University Project Details

- **Institution:** Chanakya University, Bengaluru
- **School:** School of Engineering
- **Program:** Bachelor of Computer Applications (BCA)
- **Semester:** V Semester
- **Subject:** Full Stack Development (DAT501)
- **Candidate:** Pranavraghavendra M R (Reg. No: 24UG00220)
- **GitHub Repository:** [https://github.com/PranavRaghavendraMR/transport-fleet-logistic-managment-system.git](https://github.com/PranavRaghavendraMR/transport-fleet-logistic-managment-system.git)


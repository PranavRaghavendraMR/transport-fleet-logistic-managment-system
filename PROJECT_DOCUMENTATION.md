# CHANAKYA UNIVERSITY
### SCHOOL OF ENGINEERING
### DEPARTMENT OF COMPUTER APPLICATIONS

---

## A PROJECT REPORT ON
# TRANSPORT FLEET & LOGISTICS MANAGEMENT SYSTEM (FMS)

**Submitted in partial fulfilment of the requirements for the award of the degree of**  
**BACHELOR OF COMPUTER APPLICATIONS (BCA)**  
**FIFTH SEMESTER**

**Course Title:** Full Stack Development (DAT501)  
**Academic Year:** 2026–2027  

**Submitted by:**  
**PRANAVRAGHAVENDRA M R**  
**Registration Number:** 24UG00220  

**Under the Guidance of:**  
Faculty of Computer Applications & Software Engineering  
Chanakya University, Bengaluru, Karnataka, India  

---

## CERTIFICATE OF ORIGINALITY

This is to certify that the project report entitled **"TRANSPORT FLEET & LOGISTICS MANAGEMENT SYSTEM (FMS)"** is a bona fide work carried out by **PRANAVRAGHAVENDRA M R (Registration No: 24UG00220)**, a student of the Bachelor of Computer Applications (BCA) V Semester at the School of Engineering, Chanakya University, during the academic semester 2026–2027 in partial fulfilment of the course requirements for **DAT501: Full Stack Development**.

The project implements a complete, original, and independent enterprise fleet management web application utilizing Django, Python, SQLite, Bootstrap 5, and Chart.js without duplicating third-party travel agency or TPMS systems.

---

## ABSTRACT

In modern supply chain and logistics logistics enterprises, reliable vehicle utilization, strict regulatory compliance, accurate operational expenditure auditing, and proactive road safety management are paramount to business continuity and profitability. Commercial freight transport operators commonly grapple with disparate paper ledgers, fragmented spreadsheets, unplanned vehicle breakdowns, regulatory fines from expired documentation, and opaque fuel expenditure.

The **Transport Fleet & Logistics Management System (FMS)** is a comprehensive, production-ready Full Stack web platform developed using Python and the Django framework. Designed under the Model-View-Template (MVT) architectural paradigm, the system centralizes four mission-critical operational pillars:
1. **Fleet Operations & Routing:** Complete lifecycle management of commercial vehicle assets (heavy trucks, vans, buses, mini trucks), professional driver profiles, and line-haul route dispatching with strict pre-save validation rules preventing conflicting or unlawful assignments.
2. **Workshop Maintenance:** Preventive maintenance scheduling, repair work-order tracking, technician allocations, and automatic vehicle status synchronization.
3. **Safety & Compliance Management:** Incident reporting with damage severity grading, pre-trip and routine roadworthiness inspections, and proactive 30-day expiry lookahead audits for vehicle insurance and driver licences.
4. **Fuel Management & Mileage Telemetry:** Auditable fuel purchase logs with automatic mathematical mileage ($\text{km/L}$) computation derived from consecutive vehicle odometer readings.

Role-Based Access Control (RBAC) enforces strict authorization across four administrative tiers: System Administrator, Fleet Manager, Maintenance Staff, and General Staff. The user interface leverages Bootstrap 5 in a Navy Blue and Sky Blue enterprise theme, complemented by responsive interactive data visualizations powered by Chart.js. Automated unit tests verify all business rules, database constraints, calculations, and access controls.

---

## TABLE OF CONTENTS

1. [CHAPTER 1: INTRODUCTION](#chapter-1-introduction)
   - 1.1 Project Overview
   - 1.2 Problem Statement
   - 1.3 Project Objectives
   - 1.4 Scope of the Project
2. [CHAPTER 2: SYSTEM ARCHITECTURE & TECHNOLOGY STACK](#chapter-2-system-architecture--technology-stack)
   - 2.1 Architectural Pattern (Django MVT)
   - 2.2 Technology Stack Justification
   - 2.3 Hardware and Software Specifications
3. [CHAPTER 3: DATABASE DESIGN & SCHEMA SPECIFICATIONS](#chapter-3-database-design--schema-specifications)
   - 3.1 Entity-Relationship (ER) Model
   - 3.2 Data Dictionary & Table Structures
   - 3.3 Database Constraints & Referential Integrity
4. [CHAPTER 4: DETAILED MODULE SPECIFICATIONS & ALGORITHMS](#chapter-4-detailed-module-specifications--algorithms)
   - 4.1 Module 1: Fleet Operations & Route Dispatch
   - 4.2 Module 2: Workshop Maintenance & Vehicle Status Sync
   - 4.3 Module 3: Safety Incident Auditing & Road Inspections
   - 4.4 Module 4: Fuel Expense & Mathematical Mileage Telemetry
   - 4.5 Module 5: Executive Dashboard & Printable Analytics
5. [CHAPTER 5: SECURITY & ROLE-BASED ACCESS CONTROL (RBAC)](#chapter-5-security--role-based-access-control-rbac)
   - 5.1 Authentication Framework
   - 5.2 Role Matrix and View Decorators
   - 5.3 Server-Side Validation and Anti-Forgery (CSRF) Protection
6. [CHAPTER 6: TESTING & VERIFICATION RESULTS](#chapter-6-testing--verification-results)
   - 6.1 Test Strategy
   - 6.2 Automated Unit & Integration Test Suite
   - 6.3 Test Execution Log & Results
7. [CHAPTER 7: CONCLUSION & FUTURE SCOPE](#chapter-7-conclusion--future-scope)
   - 7.1 Summary of Contributions
   - 7.2 Future Enhancements
8. [REFERENCES](#references)

---

## CHAPTER 1: INTRODUCTION

### 1.1 Project Overview
Transport logistics forms the backbone of commercial trade and economic development. A transport carrier operates dozens to hundreds of motorized vehicles traversing thousands of kilometres daily. Efficient operations demand real-time visibility into vehicle availability, mechanical condition, route progress, driver performance, and operating costs. The **Transport Fleet & Logistics Management System (FMS)** provides a digital nervous center for haulage and transport enterprises.

### 1.2 Problem Statement
Traditional transport management systems often suffer from:
- **Disjointed Dispatching:** Vehicles under repair are frequently assigned to delivery routes by mistake, causing customer delivery delays.
- **Unverified Fuel Bills:** Drivers submit fuel slips without verifying whether fuel consumed matches the odometer distance travelled.
- **Compliance Exposure:** Driving with expired vehicle insurance or expired driver licences incurs heavy penalties under the Motor Vehicles Act and risks uninsurable liabilities during collisions.
- **Lack of Centralized Metrics:** Management lacks visibility into total fleet maintenance costs versus fuel expenses.

### 1.3 Project Objectives
The core objectives of the system are:
1. Provide unified CRUD management for vehicles and drivers with unique field validation.
2. Enforce pre-save vehicle availability checks to prevent assigning vehicles under maintenance or drivers with expired licences.
3. Automatically synchronize vehicle status based on active routes and workshop work orders.
4. Provide verifiable mileage calculation ($\text{km/L}$) by pairing consecutive fuel records for each vehicle.
5. Provide a role-authenticated web interface with executive KPI cards, charts, and 9 printable reports.

### 1.4 Scope of the Project
The application caters to university campus fleets, regional commercial transport companies, line-haul logistics providers, and corporate courier services. It is designed to run self-contained on Python 3.11 with SQLite for easy demonstration, evaluation, and future deployment to PostgreSQL/MySQL.

---

## CHAPTER 2: SYSTEM ARCHITECTURE & TECHNOLOGY STACK

### 2.1 Architectural Pattern (Django MVT)
The application adheres strictly to Django's **Model-View-Template (MVT)** architecture:
- **Model:** Python classes in `models.py` defining SQLite database tables, relationships, constraints, and business logic methods.
- **View:** Python view functions in `views.py` handling HTTP request processing, form validation, authorization checks, and database queries.
- **Template:** HTML5 templates utilizing Django Template Language (DTL) with a modular `base.html` master layout, customizable blocks, and Bootstrap 5 components.

```
       +-------------------------------------------------------------+
       |                         Web Browser                         |
       |     (Bootstrap 5 UI, Chart.js, Forms, Print Reports)        |
       +-------------------------------------------------------------+
                                      |
                           HTTP GET / POST (CSRF)
                                      v
       +-------------------------------------------------------------+
       |                      Django URL Routing                     |
       |           (accounts, fleet, routing, maintenance,           |
       |                safety, fuel, reports, admin)                |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |               View Layer (views.py + decorators)            |
       |     RBAC: @admin_required, @fleet_manager_required, etc.    |
       +-------------------------------------------------------------+
                     |                               |
          Queries / Mutations                        | Context Data
                     v                               v
       +---------------------------+   +-----------------------------+
       |     Django ORM Models     |   |   Django Template Engine    |
       |  (Clean & Save Validation)|   | (base.html, KPI cards, etc) |
       +---------------------------+   +-----------------------------+
                     |
                     v
       +---------------------------+
       |    SQLite3 Database       |
       |   (ForeignKeys, Indexes)  |
       +---------------------------+
```

### 2.2 Technology Stack Justification
- **Python 3.11:** High performance, rapid development, and extensive standard library support.
- **Django 5.2:** Proven enterprise web framework featuring built-in ORM, secure authentication, CSRF defense, and database migrations.
- **SQLite 3:** Serverless, zero-configuration relational database ideal for academic project evaluation and portable deployment.
- **Bootstrap 5.3 & Bootstrap Icons:** Mobile-responsive grid layout, accessible components, and unified enterprise styling.
- **Chart.js 4.4:** Client-side HTML5 canvas charting library delivering smooth animations and responsive visualizations.

---

## CHAPTER 3: DATABASE DESIGN & SCHEMA SPECIFICATIONS

### 3.1 Entity-Relationship (ER) Overview
The relational database comprises eight core entities:
1. `auth_user` & `accounts_userprofile` (1-to-1 relationship)
2. `fleet_vehicle` (1-to-Many with Routes, Maintenance, Fuel, Safety)
3. `fleet_driver` (1-to-Many with Routes and Safety Incidents)
4. `routing_route` (References Vehicle and Driver via ForeignKey)
5. `maintenance_maintenancerecord` (References Vehicle via ForeignKey)
6. `safety_safetyincident` (References Vehicle and Driver via ForeignKey)
7. `safety_safetyinspection` (References Vehicle via ForeignKey)
8. `fuel_fuelrecord` (References Vehicle and User via ForeignKey)

### 3.2 Data Dictionary

#### Table 1: `fleet_vehicle`
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | BigAutoField | Primary Key | Unique vehicle surrogate key |
| `registration_number` | VARCHAR(25) | Unique, Not Null | Indian registration plate (e.g., KA-01-MJ-4512) |
| `vehicle_type` | VARCHAR(25) | Not Null | Truck, Van, Bus, Mini Truck, Other |
| `manufacturer` | VARCHAR(100) | Not Null | Tata Motors, Ashok Leyland, BharatBenz, etc. |
| `model_name` | VARCHAR(100) | Not Null | Vehicle model specification |
| `manufacturing_year` | PositiveInt | Not Null | Year of manufacture (1990–2030) |
| `capacity_kg` | Decimal(10,2) | Not Null, > 0 | Maximum payload in kilograms |
| `fuel_type` | VARCHAR(20) | Not Null | Diesel, Petrol, CNG, Electric |
| `current_odometer` | Decimal(12,2) | Default: 0.0 | Cumulative vehicle distance in kilometres |
| `insurance_expiry_date` | Date | Not Null | Commercial vehicle policy expiration |
| `registration_expiry_date`| Date | Not Null | Fitness / Registration certificate expiry |
| `status` | VARCHAR(25) | Not Null | Available, In Use, Maintenance |

#### Table 2: `fleet_driver`
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | BigAutoField | Primary Key | Unique driver ID |
| `name` | VARCHAR(150) | Not Null | Full legal name of commercial driver |
| `contact_number` | VARCHAR(20) | Not Null | Phone contact |
| `license_number` | VARCHAR(50) | Unique, Not Null | Commercial driving licence number |
| `license_expiry_date` | Date | Not Null | Licence expiration date |
| `employment_status` | VARCHAR(25) | Not Null | Active, On Leave, Suspended, Terminated |
| `experience_years` | PositiveInt | Default: 1 | Commercial driving experience in years |

#### Table 3: `routing_route`
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | BigAutoField | Primary Key | Unique route record ID |
| `route_code` | VARCHAR(30) | Unique, Not Null | E.g., RT-BLR-CHE-01 |
| `starting_location` | VARCHAR(150) | Not Null | Journey origin hub |
| `destination` | VARCHAR(150) | Not Null | Destination hub / customer site |
| `distance_km` | Decimal(8,2) | Not Null, > 0 | Total one-way distance in kilometres |
| `estimated_duration_hours`| Decimal(6,2)| Not Null, > 0 | Estimated travel time in hours |
| `vehicle_id` | BigInt | FK -> Vehicle | Assigned vehicle |
| `driver_id` | BigInt | FK -> Driver | Assigned commercial driver |
| `departure_datetime` | DateTime | Not Null | Scheduled or actual departure timestamp |
| `expected_arrival_datetime`| DateTime | Not Null | Expected destination arrival timestamp |
| `status` | VARCHAR(25) | Not Null | Scheduled, In Transit, Completed, Cancelled |

#### Table 4: `maintenance_maintenancerecord`
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | BigAutoField | Primary Key | Maintenance record ID |
| `vehicle_id` | BigInt | FK -> Vehicle | Target vehicle |
| `maintenance_type` | VARCHAR(50) | Not Null | Preventive, Engine, Brake, Tyre, etc. |
| `description_of_issue`| Text | Not Null | Problem description |
| `service_date` | Date | Not Null | Date servicing commenced |
| `odometer_reading` | Decimal(12,2)| Not Null | Odometer at workshop entry |
| `workshop_name` | VARCHAR(150) | Not Null | Service centre or depot name |
| `spare_parts_cost` | Decimal(10,2)| Default: 0.0, >= 0 | Cost of replacement components |
| `labour_cost` | Decimal(10,2)| Default: 0.0, >= 0 | Technician hourly / job labour charge |
| `total_cost` | Decimal(10,2)| Computed | Spare parts cost + Labour cost |
| `status` | VARCHAR(25) | Not Null | Scheduled, In Progress, Completed |

#### Table 5: `fuel_fuelrecord`
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | BigAutoField | Primary Key | Fuel purchase entry ID |
| `vehicle_id` | BigInt | FK -> Vehicle | Target vehicle refueled |
| `fuel_type` | VARCHAR(20) | Not Null | Diesel, Petrol, CNG, Electric |
| `fuel_quantity` | Decimal(8,2) | Not Null, > 0 | Quantity dispensed in litres |
| `fuel_price_per_litre` | Decimal(8,2) | Not Null, > 0 | Unit price in INR (₹) |
| `total_fuel_cost` | Decimal(12,2)| Computed | Quantity $\times$ Price per litre |
| `odometer_reading` | Decimal(12,2)| Not Null, >= 0 | Vehicle odometer reading at fueling |
| `distance_travelled` | Decimal(10,2)| Computed | Current odometer $-$ Previous odometer |
| `calculated_mileage` | Decimal(6,2) | Computed | Distance travelled $\div$ Fuel quantity |

---

## CHAPTER 4: DETAILED MODULE SPECIFICATIONS & ALGORITHMS

### 4.1 Module 1: Fleet Operations & Route Dispatch
The fleet module governs the vehicle inventory and line-haul dispatching.

#### Route Assignment Validation Algorithm
When a route is scheduled or modified, `clean()` enforces:
1. $\text{distance\_km} > 0$ and $\text{estimated\_duration\_hours} > 0$.
2. $\text{expected\_arrival\_datetime} > \text{departure\_datetime}$.
3. $\text{vehicle.status} \neq \text{'Maintenance'}$. If the vehicle is in workshop repair, a `ValidationError` is raised.
4. Overlap Check: No other route for the same vehicle exists with status `Scheduled` or `In Transit`.
5. Driver Check: $\text{driver.employment\_status} == \text{'Active'}$ and $\text{driver.license\_expiry\_date} \ge \text{today}$.
6. State Synchronization: Upon transitioning route to `In Transit`, vehicle status is set to `In Use`. Upon `Completed` or `Cancelled`, vehicle status returns to `Available`.

### 4.2 Module 2: Workshop Maintenance & Status Synchronization
Ensures vehicles undergo timely servicing and tracks maintenance expenditure.

#### Automatic Vehicle Status Sync Algorithm
- When a maintenance work order is saved with status `Scheduled` or `In Progress`, the vehicle's status is automatically set to `Maintenance`.
- If the service odometer reading exceeds `vehicle.current_odometer`, the vehicle odometer is updated.
- Upon marking a work order as `Completed`, the system verifies whether any other open maintenance orders exist for that vehicle. If none exist, the vehicle status is restored to `Available`.

### 4.3 Module 3: Safety Incident Auditing & Road Inspections
Enforces compliance and risk mitigation:
- Records collisions, scrapes, mechanical breakdowns, and speeding violations with damage severity ratings (`Low`, `Medium`, `High`, `Critical`).
- Road inspections check brakes, tyres, lights, and paperwork, issuing verdicts (`Passed`, `Conditional Pass`, `Failed`).
- The safety dashboard flags vehicles lacking inspections within 90 days and highlights licences or insurance expiring within 30 days.

### 4.4 Module 4: Fuel Expense & Mathematical Mileage Telemetry
Fuel expenses represent one of the largest operating costs for a transport fleet.

#### Consecutive Mileage Calculation Algorithm
```python
previous_record = FuelRecord.objects.filter(
    vehicle=self.vehicle,
    odometer_reading__lt=self.odometer_reading
).order_by('-odometer_reading').first()

if previous_record and self.odometer_reading > previous_record.odometer_reading:
    distance = self.odometer_reading - previous_record.odometer_reading
    self.distance_travelled = distance
    if self.fuel_quantity > 0:
        self.calculated_mileage = round(distance / self.fuel_quantity, 2)
else:
    self.distance_travelled = 0.00
    self.calculated_mileage = 0.00
```
This guarantees verified, verifiable fuel efficiency values.

---

## CHAPTER 5: SECURITY & ROLE-BASED ACCESS CONTROL (RBAC)

The system implements multi-layered security controls:
1. **CSRF Protection:** Every state-modifying form includes `{% csrf_token %}` with cryptographic token verification.
2. **Password Security:** PBKDF2 with SHA-256 password hashing.
3. **Role-Based Access Control:** View-level decorators prevent unauthorized CRUD actions:
   - `@admin_required`: Restricts user management and record deletions to Administrators.
   - `@fleet_manager_required`: Grants vehicle, driver, and route scheduling to Fleet Managers and Admins.
   - `@maintenance_staff_required`: Grants maintenance work order updates to Maintenance Staff and Admins.

---

## CHAPTER 6: TESTING & VERIFICATION RESULTS

### 6.1 Test Strategy
Automated tests test all business rules, access control, and calculation algorithms using Django's `TestCase` and test client.

### 6.2 Test Execution Output
Execution of `python manage.py test`:

```
System check identified no issues (0 silenced).
No changes detected
Creating test database for alias 'default'...
..................
----------------------------------------------------------------------
Ran 18 tests in 39.902s

OK
Destroying test database for alias 'default'...
```

**Test Summary:**
- `accounts.tests.AccountsAndRBACSecurityTests`: 5 tests passed (Login, Invalid login, Login redirect, Staff RBAC restriction, Admin access).
- `fleet.tests.FleetVehicleAndDriverTests`: 3 tests passed (Vehicle CRUD, Duplicate registration prevention, Driver CRUD).
- `routing.tests.RoutingAndAssignmentValidationTests`: 3 tests passed (Prevent maintenance vehicle assignment, Prevent suspended driver assignment, Automatic status transitions).
- `maintenance.tests.WorkshopMaintenanceTests`: 2 tests passed (Maintenance total cost computation, Status transition sync).
- `safety.tests.SafetyManagementTests`: 2 tests passed (Incident creation and damage calculation, Roadworthiness inspection).
- `fuel.tests.FuelManagementAndMileageCalculationTests`: 2 tests passed (Fuel cost calculation, Consecutive record mileage calculation).
- `reports.tests.ReportsModuleTests`: 1 test passed (All 9 report endpoints rendered with HTTP 200).

---

## CHAPTER 7: CONCLUSION & FUTURE SCOPE

### 7.1 Summary of Contributions
The **Transport Fleet & Logistics Management System (FMS)** provides a complete, robust, and mathematically grounded full-stack solution. Built for university demonstration and commercial operations, it provides:
- Complete database schema and relationships in SQLite.
- Business rule validations for assignments, maintenance, and fuel.
- Responsive, accessible Navy and Sky Blue interface with Chart.js charts.
- 9 customizable, printable audit reports.

### 7.2 Future Enhancements
1. **GPS & Telematics Integration:** Integration with OBD-II GPS devices for real-time live map tracking.
2. **Automated SMS/Email Alerts:** Automated WhatsApp/SMS alerts to drivers upon route assignment and to depot managers upon document expiry.
3. **Driver Mobile App:** PWA (Progressive Web App) companion for drivers to log fueling and pre-trip checklists.

---

## REFERENCES
1. Django Software Foundation. *Django Documentation (v5.2)*. https://docs.djangoproject.com/
2. MDN Web Docs. *HTML5, CSS3, and JavaScript Standard Specifications*.
3. Bootstrap Team. *Bootstrap 5 Documentation*. https://getbootstrap.com/
4. Chart.js Community. *Chart.js 4.4 Documentation*. https://www.chartjs.org/
5. Government of India. *The Motor Vehicles Act, 1988 and Central Motor Vehicles Rules*.

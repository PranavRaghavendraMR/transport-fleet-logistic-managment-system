# TRANSPORT FLEET & LOGISTICS MANAGEMENT SYSTEM (FMS)
## University Project Demonstration Guide & Viva Voce Handbook

**Candidate:** Pranavraghavendra M R  
**Registration Number:** 24UG00220  
**University:** Chanakya University  
**Department:** School of Engineering  
**Degree & Course:** BCA V Semester &bull; Full Stack Development (DAT501)  

---

## 1. Quick Launch Checklist

To start the live project demonstration before the viva examiners:

1. Open PowerShell or Command Prompt in the project folder:
   ```bash
   cd d:\pranav\transport-fms
   ```
2. Double click `run.bat` or execute:
   ```bash
   python manage.py runserver
   ```
3. Open your browser at: **`http://127.0.0.1:8000/`**

---

## 2. Recommended Live Demonstration Sequence

Follow this structured 6-step walkthrough during your evaluation:

### Step 1: Authentication & Role Demonstration
- Go to `http://127.0.0.1:8000/login/`.
- Show the clean login page with role credentials prominently noted in the footer.
- Log in as **`admin`** (Password: `Admin@123`).
- Point out the academic banner in the top navigation:
  `Chanakya University • School of Engineering • Student: Pranavraghavendra M R (24UG00220)`.
- Open **Staff & Roles** (`/users/`): Show the 4 user tiers and explain how the system uses custom Django decorators (`@admin_required`, `@fleet_manager_required`, `@maintenance_staff_required`) to secure views.

### Step 2: Executive Dashboard & Chart Telemetry
- Navigate to the **Executive Dashboard** (`/`).
- Walk through the **10 KPI Cards**:
  1. Total Fleet (10)
  2. Available (Ready)
  3. In Use (On Road)
  4. Maintenance (In Workshop)
  5. Active Drivers
  6. Active Routes
  7. Pending Maintenance
  8. Total Fuel Expenses (₹)
  9. Total Maintenance Costs (₹)
  10. Open Safety Incidents
- Demonstrate the **Chart.js Visualizations**:
  - *Fleet Status Distribution* (Doughnut chart)
  - *Monthly Operational Expenses Trend* (Bar chart comparing Fuel vs Maintenance across past 6 months)
- Highlight the **Compliance Watchlist**: Show automatic warnings for vehicle insurance and driver licences expiring within 30 days.

### Step 3: Fleet Operations & Route Dispatch
- Click **Vehicles** (`/fleet/vehicles/`):
  - Filter by Vehicle Type (`Truck`, `Van`, `Mini Truck`, `Bus`).
  - Search by registration number (e.g. `KA-01-MJ-4512`).
  - Open a vehicle dossier: Show tabs for Routes, Workshop History, Fuel Logs, and Safety.
- Click **Routing & Dispatch** (`/routing/`):
  - Show active transit routes (`In Transit`, `Scheduled`).
  - Click on route `RT-BLR-CHE-01`. Demonstrate the quick status action button: click **Mark as Completed**. Show how the vehicle's status automatically updates back to `Available`.
  - Demonstrate **Validation Safeguards**: Attempt to schedule a route with vehicle `KA-04-HY-9988` (which is under Maintenance). Show the red validation error preventing the dispatch!

### Step 4: Workshop Maintenance & Status Synchronization
- Navigate to **Workshop Dashboard** (`/maintenance/dashboard/`):
  - Point out the *Overdue Vehicle Servicing Alert* box.
  - Review the expense breakdown by maintenance category (Preventive, Brake, Engine, Tyre).
- Go to **Service Logs** (`/maintenance/`):
  - Open an in-progress work order (e.g. `KA-04-HY-9988`).
  - Click **Complete Work Order** modal. Enter notes and submit.
  - Show how the vehicle status is automatically restored to `Available`.

### Step 5: Safety Incidents & Road Inspections
- Navigate to **Safety Dashboard** (`/safety/dashboard/`):
  - Review Open vs Resolved incidents.
  - Show the *Vehicles Requiring Safety Inspection* table (vehicles without inspections in 90 days).
  - Open an incident file (`/safety/incidents/`): Show damage severity, estimated loss cost, and corrective actions taken.
  - Open an inspection sheet (`/safety/inspections/`): Show multi-point checks for Brakes, Tyres, Lights, and Documents.

### Step 6: Fuel Management & Mathematical Mileage
- Navigate to **Fuel Analytics** (`/fuel/dashboard/`):
  - Review total litres consumed and average fleet mileage.
  - Point out the *Vehicle-wise Fuel Consumption & Mileage Analysis* table.
- Open a fuel record (`/fuel/`):
  - Explain the **Mileage Formula**:
    $$\text{Mileage (km/L)} = \frac{\text{Current Odometer} - \text{Previous Odometer}}{\text{Fuel Quantity}}$$
  - Show how the system queries the previous consecutive fuel record for the vehicle and calculates the exact fuel economy.

### Step 7: Printable Audit Reports
- Go to **Reports Center** (`/reports/`):
  - Open any report (e.g. **Vehicle Inventory Report**, **Maintenance Expense Report**, or **Vehicle Mileage Report**).
  - Apply filters (Vehicle, Status, Date).
  - Click the **Print / Export PDF** button: Show how `@media print` hides the sidebar and top navigation and formats a clean formal document suitable for paper submission or PDF export.

---

## 3. Likely Viva Voce Questions & Model Answers

### Q1: What is the Model-View-Template (MVT) pattern in Django, and how did you use it?
**Answer:**  
In Django, MVT structures web applications into three decoupled layers:
- **Model (`models.py`):** Represents the database schema and business logic constraints (e.g. `Vehicle`, `Route`, `FuelRecord`).
- **View (`views.py`):** The controller logic that processes incoming HTTP requests, interacts with the ORM, executes business rules, and passes context data to the template.
- **Template (`templates/`):** The presentation layer written in HTML5 and Django Template Language (DTL) using inheritance (`base.html`) and Bootstrap 5 for responsive display.

### Q2: How does the system calculate fuel mileage, and what assumptions are made?
**Answer:**  
The mileage calculation is implemented inside `FuelRecord.calculate_mileage_from_previous()`. When a fuel entry is saved:
1. The system queries the immediately preceding fuel record for that same vehicle where `odometer_reading < current_odometer`.
2. It calculates distance run: $\text{Distance} = \text{Current Odometer} - \text{Previous Odometer}$.
3. It derives mileage: $\text{Mileage (km/L)} = \frac{\text{Distance}}{\text{Fuel Quantity}}$.
4. If it is the first fuel purchase for that vehicle (no preceding record), mileage is recorded as `0.00` until a baseline is established.

### Q3: How do you prevent assigning a vehicle under maintenance or a driver with an expired licence?
**Answer:**  
We implement pre-save validation inside `Route.clean()` in `routing/models.py`:
- We check `if self.vehicle.status == Vehicle.STATUS_MAINTENANCE: raise ValidationError(...)`
- We also verify `self.driver.is_license_expired` and check that the driver is `Active`.
- Furthermore, we verify that neither the vehicle nor the driver is already assigned to another overlapping route with status `Scheduled` or `In Transit`.

### Q4: How is Role-Based Access Control (RBAC) enforced? Is it just hidden from the UI?
**Answer:**  
No, hiding navigation links is merely for UI ergonomics. True security is enforced on the server side using custom Python view decorators:
- `@admin_required`: Restricts deletion and user administration views to users with `role == 'ADMIN'` or `is_superuser`.
- `@fleet_manager_required`: Restricts vehicle/driver editing and route dispatching to `ADMIN` and `FLEET_MANAGER`.
- `@maintenance_staff_required`: Restricts workshop logs to `ADMIN` and `MAINTENANCE_STAFF`.
If an unauthorized user manually types the URL endpoint, the decorator catches it, displays a message, and redirects them.

### Q5: How does vehicle status synchronize with routes and maintenance?
**Answer:**  
Synchronization is automated in the model `save()` methods:
- When a `Route` status becomes `In Transit`, `vehicle.status` is set to `In Use`. When `Completed`, it returns to `Available`.
- When a `MaintenanceRecord` is set to `Scheduled` or `In Progress`, `vehicle.status` is set to `Maintenance`. When `Completed`, it verifies whether any other open maintenance tickets exist; if none exist, `vehicle.status` returns to `Available`.

### Q6: Why did you choose SQLite for this university project?
**Answer:**  
SQLite is built into Python, requires zero external daemon processes, stores data in an atomic, portable single file (`db.sqlite3`), and fully supports transactions and ForeignKey constraints. Because Django uses an Object-Relational Mapper (ORM), the exact same code can be ported to PostgreSQL or MySQL simply by changing the `DATABASES` dictionary in `settings.py` without modifying any view or model code.

### Q7: What automated tests did you write, and how do you run them?
**Answer:**  
We wrote 18 automated unit and integration tests across all modules covering authentication, vehicle and driver CRUD, assignment validations, maintenance calculations, safety records, consecutive fuel mileage formulas, and report views. They are executed via `python manage.py test`.

---

## 4. Student & Course Attribution Summary

- **Project:** Transport Fleet & Logistics Management System (FMS)
- **Student Name:** Pranavraghavendra M R
- **Registration Number:** 24UG00220
- **Institution:** Chanakya University, Bengaluru
- **School:** School of Engineering
- **Program:** Bachelor of Computer Applications (BCA)
- **Semester & Course:** V Semester &bull; Full Stack Development (DAT501)
- **Year:** 2026–2027

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, datetime, timedelta
from decimal import Decimal

from accounts.models import UserProfile
from fleet.models import Vehicle, Driver
from routing.models import Route
from maintenance.models import MaintenanceRecord
from safety.models import SafetyIncident, SafetyInspection
from fuel.models import FuelRecord


class Command(BaseCommand):
    help = "Seed realistic demonstration data for Transport Fleet Management System"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Clearing existing data and seeding fresh demonstration dataset..."))

        # Clean old demo records
        FuelRecord.objects.all().delete()
        SafetyIncident.objects.all().delete()
        SafetyInspection.objects.all().delete()
        MaintenanceRecord.objects.all().delete()
        Route.objects.all().delete()
        Driver.objects.all().delete()
        Vehicle.objects.all().delete()

        # 1. Create Demo Users
        users_data = [
            ('admin', 'Admin@123', 'admin@transportfms.edu', 'Pranavraghavendra', 'M R', UserProfile.ROLE_ADMIN, 'EMP0001', '+91 98450 11223', 'Executive Fleet Directorate', True),
            ('manager', 'Manager@123', 'manager@transportfms.edu', 'Rajesh', 'Kumar', UserProfile.ROLE_FLEET_MANAGER, 'EMP0002', '+91 97410 44556', 'Fleet Routing & Operations', False),
            ('mechanic', 'Mechanic@123', 'mechanic@transportfms.edu', 'Suresh', 'Babu', UserProfile.ROLE_MAINTENANCE_STAFF, 'EMP0003', '+91 98860 77889', 'Central Maintenance Depot', False),
            ('staff', 'Staff@123', 'staff@transportfms.edu', 'Ananya', 'Sharma', UserProfile.ROLE_GENERAL_STAFF, 'EMP0004', '+91 94480 33445', 'Logistics Operations Support', False),
        ]

        users_map = {}
        for uname, pwd, email, fname, lname, role, emp_id, phone, dept, is_super in users_data:
            user, created = User.objects.get_or_create(username=uname, defaults={'email': email, 'first_name': fname, 'last_name': lname, 'is_staff': True, 'is_superuser': is_super})
            user.set_password(pwd)
            user.save()
            profile = getattr(user, 'profile', None)
            if not profile:
                profile = UserProfile.objects.create(user=user, role=role, employee_id=emp_id, phone=phone, department=dept)
            else:
                profile.role = role
                profile.employee_id = emp_id
                profile.phone = phone
                profile.department = dept
                profile.save()
            users_map[uname] = user
            self.stdout.write(self.style.SUCCESS(f"  User ready: {uname} (Role: {role})"))

        admin_user = users_map['admin']

        # 2. Create Vehicles (10 Indian Commercial Vehicles)
        today = date.today()
        vehicles_data = [
            ('KA-01-MJ-4512', Vehicle.TYPE_TRUCK, 'Tata Motors', 'Prima 4440.S Hauler', 2022, 28000.0, Vehicle.FUEL_DIESEL, 74200.0, today + timedelta(days=180), today + timedelta(days=320), Vehicle.STATUS_AVAILABLE),
            ('KA-05-AB-8910', Vehicle.TYPE_TRUCK, 'Ashok Leyland', 'AVTR 2820 HG', 2021, 20000.0, Vehicle.FUEL_DIESEL, 96500.0, today + timedelta(days=220), today + timedelta(days=190), Vehicle.STATUS_AVAILABLE),
            ('MH-12-PQ-3344', Vehicle.TYPE_TRUCK, 'BharatBenz', '2823R Heavy Cargo', 2023, 19000.0, Vehicle.FUEL_DIESEL, 48300.0, today + timedelta(days=15), today + timedelta(days=280), Vehicle.STATUS_AVAILABLE),
            ('TN-09-BK-6677', Vehicle.TYPE_VAN, 'Force Motors', 'Traveller Delivery Cargo', 2022, 3500.0, Vehicle.FUEL_DIESEL, 62100.0, today + timedelta(days=95), today + timedelta(days=110), Vehicle.STATUS_AVAILABLE),
            ('DL-1L-AA-5544', Vehicle.TYPE_MINI_TRUCK, 'Mahindra', 'Bolero Maxi Truck Plus', 2023, 1200.0, Vehicle.FUEL_DIESEL, 31400.0, today + timedelta(days=140), today + timedelta(days=360), Vehicle.STATUS_AVAILABLE),
            ('KA-03-TC-1122', Vehicle.TYPE_MINI_TRUCK, 'Tata Motors', 'Ace Gold EV', 2024, 1000.0, Vehicle.FUEL_ELECTRIC, 14200.0, today + timedelta(days=300), today + timedelta(days=400), Vehicle.STATUS_AVAILABLE),
            ('KA-04-HY-9988', Vehicle.TYPE_BUS, 'Eicher', 'Skyline Pro 3009 Staff Bus', 2021, 4500.0, Vehicle.FUEL_CNG, 85600.0, today + timedelta(days=60), today + timedelta(days=150), Vehicle.STATUS_MAINTENANCE),
            ('TS-07-UA-7788', Vehicle.TYPE_TRUCK, 'Ashok Leyland', 'Boss 1415 Tipper', 2022, 14000.0, Vehicle.FUEL_DIESEL, 59800.0, today + timedelta(days=115), today + timedelta(days=240), Vehicle.STATUS_AVAILABLE),
            ('KA-51-EX-2020', Vehicle.TYPE_VAN, 'Tata Motors', 'Winger Cargo Van', 2023, 2000.0, Vehicle.FUEL_PETROL, 28700.0, today + timedelta(days=20), today + timedelta(days=310), Vehicle.STATUS_AVAILABLE),
            ('MH-04-KL-9009', Vehicle.TYPE_TRUCK, 'Eicher', 'Pro 6028 Haulage', 2020, 24000.0, Vehicle.FUEL_DIESEL, 118400.0, today - timedelta(days=5), today + timedelta(days=80), Vehicle.STATUS_AVAILABLE),
        ]

        vehicles_map = {}
        for reg, vtype, mfg, model, year, cap, fuel, odo, ins_exp, reg_exp, stat in vehicles_data:
            v = Vehicle.objects.create(
                registration_number=reg,
                vehicle_type=vtype,
                manufacturer=mfg,
                model_name=model,
                manufacturing_year=year,
                capacity_kg=cap,
                fuel_type=fuel,
                current_odometer=odo,
                insurance_expiry_date=ins_exp,
                registration_expiry_date=reg_exp,
                status=stat,
                notes="Assigned to corporate linehaul operations depot."
            )
            vehicles_map[reg] = v
        self.stdout.write(self.style.SUCCESS(f"  Created {len(vehicles_map)} vehicles."))

        # 3. Create Drivers (7 Professional Indian Drivers)
        drivers_data = [
            ('Ramesh Gowda', '+91 98440 12345', 'KA0120180012345', today + timedelta(days=400), 'Koramangala, Bengaluru, Karnataka', Driver.STATUS_ACTIVE, 12, '+91 98440 12399'),
            ('Sanjay Patil', '+91 97410 56789', 'MH1220190054321', today + timedelta(days=280), 'Hadapsar, Pune, Maharashtra', Driver.STATUS_ACTIVE, 8, '+91 97410 56799'),
            ('Muthukumar S', '+91 98860 34567', 'TN0920170098765', today + timedelta(days=190), 'Guindy, Chennai, Tamil Nadu', Driver.STATUS_ACTIVE, 15, '+91 98860 34599'),
            ('Harpreet Singh', '+91 94480 78901', 'DL1420200034567', today + timedelta(days=15), 'Transport Nagar, New Delhi', Driver.STATUS_ACTIVE, 10, '+91 94480 78999'),
            ('Anil Chawla', '+91 99000 23456', 'TS0720210087654', today + timedelta(days=520), 'Kukatpally, Hyderabad, Telangana', Driver.STATUS_ACTIVE, 6, '+91 99000 23499'),
            ('Mahesh Naik', '+91 98450 67890', 'KA0520160045678', today + timedelta(days=320), 'Jayanagar, Bengaluru, Karnataka', Driver.STATUS_ON_LEAVE, 9, '+91 98450 67899'),
            ('Sunil Verma', '+91 97310 89012', 'MH0420150023456', today - timedelta(days=10), 'Thane West, Mumbai, Maharashtra', Driver.STATUS_SUSPENDED, 11, '+91 97310 89099'),
        ]

        drivers_list = []
        for name, phone, lic, lic_exp, addr, stat, exp, emg in drivers_data:
            d = Driver.objects.create(
                name=name,
                contact_number=phone,
                license_number=lic,
                license_expiry_date=lic_exp,
                address=addr,
                employment_status=stat,
                experience_years=exp,
                emergency_contact=emg
            )
            drivers_list.append(d)
        self.stdout.write(self.style.SUCCESS(f"  Created {len(drivers_list)} drivers."))

        # 4. Create Transportation Routes (8 Routes with distinct active drivers/vehicles)
        now = timezone.now()
        routes_data = [
            ('RT-BLR-CHE-01', 'Bengaluru Central Depot', 'Chennai Harbor Terminal', Decimal('348.0'), Decimal('7.5'), 'Electronic hardware and industrial machinery components.', vehicles_map['KA-05-AB-8910'], drivers_list[0], now - timedelta(hours=3), now + timedelta(hours=4, minutes=30), Route.STATUS_IN_TRANSIT),
            ('RT-BLR-HYD-02', 'Bengaluru Electronic City', 'Hyderabad Logistics Park', Decimal('570.0'), Decimal('10.5'), 'High-priority e-commerce shipments.', vehicles_map['DL-1L-AA-5544'], drivers_list[1], now - timedelta(hours=5), now + timedelta(hours=5, minutes=30), Route.STATUS_IN_TRANSIT),
            ('RT-DEL-JAI-04', 'Delhi Aerocity Hub', 'Jaipur Industrial Area', Decimal('270.0'), Decimal('5.5'), 'Retail textile consignments.', vehicles_map['TS-07-UA-7788'], drivers_list[3], now + timedelta(hours=6), now + timedelta(hours=12), Route.STATUS_SCHEDULED),
            ('RT-BLR-MYS-05', 'Bengaluru Peenya Depot', 'Mysuru Logistics Hub', Decimal('145.0'), Decimal('3.0'), 'Fast-moving consumer goods (FMCG).', vehicles_map['MH-12-PQ-3344'], drivers_list[4], now + timedelta(days=1, hours=4), now + timedelta(days=1, hours=7), Route.STATUS_SCHEDULED),
            ('RT-PUN-BOM-03', 'Pune Bhosari Hub', 'Nhava Sheva Port, Mumbai', Decimal('155.0'), Decimal('3.5'), 'Automotive spare parts pallet consignment.', vehicles_map['KA-01-MJ-4512'], drivers_list[2], now - timedelta(days=2, hours=8), now - timedelta(days=2, hours=4), Route.STATUS_COMPLETED),
            ('RT-CHE-CBE-06', 'Chennai Ambattur Hub', 'Coimbatore Tidel Park', Decimal('505.0'), Decimal('9.0'), 'Engineering tools and raw components.', vehicles_map['KA-51-EX-2020'], drivers_list[2], now - timedelta(days=4, hours=12), now - timedelta(days=4, hours=3), Route.STATUS_COMPLETED),
            ('RT-BLR-GOA-07', 'Bengaluru Hub', 'Vasco Da Gama Port, Goa', Decimal('590.0'), Decimal('12.0'), 'Frozen food refrigerated logistics consignment.', vehicles_map['KA-01-MJ-4512'], drivers_list[1], now - timedelta(days=6), now - timedelta(days=5, hours=12), Route.STATUS_COMPLETED),
            ('RT-MUM-AHD-08', 'Mumbai Bhiwandi Hub', 'Ahmedabad GIDC Park', Decimal('525.0'), Decimal('10.0'), 'Pharma medicines and medical equipment.', vehicles_map['MH-04-KL-9009'], drivers_list[0], now - timedelta(days=8), now - timedelta(days=7, hours=14), Route.STATUS_COMPLETED),
        ]

        for code, orig, dest, dist, dur, desc, veh, drv, dep, arr, stat in routes_data:
            r = Route(
                route_code=code,
                starting_location=orig,
                destination=dest,
                distance_km=dist,
                estimated_duration_hours=dur,
                description=desc,
                vehicle=veh,
                driver=drv,
                departure_datetime=dep,
                expected_arrival_datetime=arr,
                status=stat
            )
            if stat == Route.STATUS_COMPLETED:
                r.actual_arrival_datetime = arr
            r.save()
        self.stdout.write(self.style.SUCCESS(f"  Created 8 transportation routes."))

        # 5. Create Workshop Maintenance Records (7 Records)
        maint_data = [
            (vehicles_map['KA-04-HY-9988'], MaintenanceRecord.TYPE_ENGINE, 'Engine overheating and coolant leakage diagnosed during intercity charter.', today - timedelta(days=2), today + timedelta(days=6), Decimal('85600.0'), 'Ravi Shankaran', 'Eicher Express Workshop - Yeshwanthpur', Decimal('14500.00'), Decimal('4200.00'), MaintenanceRecord.STATUS_IN_PROGRESS),
            (vehicles_map['KA-01-MJ-4512'], MaintenanceRecord.TYPE_PREVENTIVE, 'Scheduled 70,000 km general servicing, engine oil filter change, fluid top-up.', today - timedelta(days=12), today + timedelta(days=80), Decimal('72100.0'), 'Murugan K', 'Tata Authorized Commercial Service, Hosur', Decimal('8900.00'), Decimal('2600.00'), MaintenanceRecord.STATUS_COMPLETED),
            (vehicles_map['KA-05-AB-8910'], MaintenanceRecord.TYPE_BRAKE, 'Brake pad renewal, drum machining, and pneumatic air valve replacement.', today - timedelta(days=25), today + timedelta(days=65), Decimal('94200.0'), 'Devendra Rao', 'Ashok Leyland Workshop, Peenya', Decimal('12400.00'), Decimal('3500.00'), MaintenanceRecord.STATUS_COMPLETED),
            (vehicles_map['MH-12-PQ-3344'], MaintenanceRecord.TYPE_TYRE, 'Front steer axle tyres replaced due to tread depth wear (Michelin X Multi).', today - timedelta(days=40), today + timedelta(days=120), Decimal('45800.0'), 'Anil Shinde', 'BharatBenz Service Depot, Pune', Decimal('38000.00'), Decimal('2000.00'), MaintenanceRecord.STATUS_COMPLETED),
            (vehicles_map['TS-07-UA-7788'], MaintenanceRecord.TYPE_ELECTRICAL, 'Alternator rewinding and starter motor solenoid replacement.', today - timedelta(days=18), today + timedelta(days=75), Decimal('58400.0'), 'Vikram Reddy', 'Sri Sai Auto Electric Works, Hyderabad', Decimal('6200.00'), Decimal('1800.00'), MaintenanceRecord.STATUS_COMPLETED),
            (vehicles_map['KA-51-EX-2020'], MaintenanceRecord.TYPE_INSPECTION, 'Periodic 30,000 km pre-monsoon safety inspection and wheel alignment.', today + timedelta(days=5), today + timedelta(days=95), Decimal('28700.0'), 'Gopal Krishna', 'Central Depot Workshop - Bay 3', Decimal('1500.00'), Decimal('1200.00'), MaintenanceRecord.STATUS_SCHEDULED),
            (vehicles_map['MH-04-KL-9009'], MaintenanceRecord.TYPE_BODY, 'Cabin bumper alignment and side fender dent repair after loading bay scrape.', today - timedelta(days=60), today + timedelta(days=30), Decimal('115000.0'), 'Nilesh Mane', 'Prabhat Body Works, Thane', Decimal('7500.00'), Decimal('4500.00'), MaintenanceRecord.STATUS_COMPLETED),
        ]

        for veh, mtype, desc, sdate, ndate, odo, tech, wshop, spare, labour, stat in maint_data:
            MaintenanceRecord.objects.create(
                vehicle=veh,
                maintenance_type=mtype,
                description_of_issue=desc,
                service_date=sdate,
                next_service_date=ndate,
                odometer_reading=odo,
                technician_name=tech,
                workshop_name=wshop,
                spare_parts_cost=spare,
                labour_cost=labour,
                status=stat,
                work_completion_notes="Work executed as per OEM standards." if stat == MaintenanceRecord.STATUS_COMPLETED else ""
            )
        self.stdout.write(self.style.SUCCESS(f"  Created 7 workshop maintenance records."))

        # 6. Create Safety Incidents & Inspections
        incidents_data = [
            ('INC-2026-001', vehicles_map['KA-05-AB-8910'], drivers_list[0], today - timedelta(days=8), 'NH-48 near Krishnagiri Toll Plaza', SafetyIncident.TYPE_MINOR_SCRAPE, 'Rear bumper grazed by overtaking auto-rickshaw during slow moving toll queue.', SafetyIncident.SEVERITY_LOW, Decimal('3500.00'), 'Local settlement completed, paint touch-up authorized at next service.', SafetyIncident.STATUS_RESOLVED),
            ('INC-2026-002', vehicles_map['MH-12-PQ-3344'], drivers_list[1], today - timedelta(days=18), 'Pune-Solapur Highway KM 44', SafetyIncident.TYPE_BREAKDOWN, 'Pneumatic air brake hose leak caused vehicle to stall safely in emergency lane.', SafetyIncident.SEVERITY_MEDIUM, Decimal('6800.00'), 'Roadside mobile recovery dispatched; hose replaced on site within 2.5 hours.', SafetyIncident.STATUS_RESOLVED),
            ('INC-2026-003', vehicles_map['KA-04-HY-9988'], drivers_list[2], today - timedelta(days=3), 'Nelamangala Highway Flyover', SafetyIncident.TYPE_BREAKDOWN, 'Engine coolant temp gauge warning light triggered; vehicle parked at safe bay.', SafetyIncident.SEVERITY_HIGH, Decimal('18700.00'), 'Vehicle towed to Yeshwanthpur workshop for radiator inspection.', SafetyIncident.STATUS_INVESTIGATING),
            ('INC-2026-004', vehicles_map['DL-1L-AA-5544'], drivers_list[3], today - timedelta(days=1), 'Jaipur Highway Exit 7', SafetyIncident.TYPE_OVERSPEEDING, 'Highway patrol automated speed camera logged 78 km/h in a 60 km/h zone.', SafetyIncident.SEVERITY_LOW, Decimal('2000.00'), 'Traffic challan paid online; driver counseled on speed limiter compliance.', SafetyIncident.STATUS_RESOLVED),
            ('INC-2026-005', vehicles_map['MH-04-KL-9009'], drivers_list[4], today - timedelta(days=35), 'Bhiwandi Warehousing Hub, Gate 4', SafetyIncident.TYPE_CARGO_DAMAGE, 'Forklift operator misjudged pallet clearance, causing minor tear in carton pallet wrapping.', SafetyIncident.SEVERITY_LOW, Decimal('4200.00'), 'Cargo repacked and surveyed; insurance claim filed with consignee acknowledgement.', SafetyIncident.STATUS_CLOSED),
            ('INC-2026-006', vehicles_map['TS-07-UA-7788'], drivers_list[4], today - timedelta(days=14), 'Shamshabad Airport Cargo Road', SafetyIncident.TYPE_NEAR_MISS, 'Two-wheeler suddenly veered into lane; driver executed emergency controlled braking safely.', SafetyIncident.SEVERITY_LOW, Decimal('0.00'), 'Dashcam footage preserved; commended driver for defensive driving.', SafetyIncident.STATUS_CLOSED),
        ]

        for iid, veh, drv, idate, loc, itype, desc, sev, cost, act, stat in incidents_data:
            SafetyIncident.objects.create(
                incident_id=iid,
                vehicle=veh,
                driver=drv,
                incident_date=idate,
                incident_location=loc,
                incident_type=itype,
                description=desc,
                damage_severity=sev,
                estimated_damage_cost=cost,
                action_taken=act,
                status=stat
            )
        self.stdout.write(self.style.SUCCESS(f"  Created 6 safety incidents."))

        inspections_data = [
            ('INSP-2026-001', vehicles_map['KA-01-MJ-4512'], today - timedelta(days=10), 'C. M. Nanjappa', 'Pass', 'Pass', 'Pass', 'Valid', SafetyInspection.RESULT_PASSED, 'Brake linings, tyre pressure and documents verified in excellent order.'),
            ('INSP-2026-002', vehicles_map['KA-05-AB-8910'], today - timedelta(days=22), 'C. M. Nanjappa', 'Pass', 'Pass', 'Attention Needed', 'Valid', SafetyInspection.RESULT_CONDITIONAL, 'Left fog light bulb dim; replaced immediately.'),
            ('INSP-2026-003', vehicles_map['MH-12-PQ-3344'], today - timedelta(days=14), 'Rakesh Deshmukh', 'Pass', 'Pass', 'Pass', 'Expiring Soon', SafetyInspection.RESULT_CONDITIONAL, 'Insurance expiring in 15 days; alerted fleet accounts.'),
            ('INSP-2026-004', vehicles_map['TN-09-BK-6677'], today - timedelta(days=5), 'V. Soundararajan', 'Pass', 'Pass', 'Pass', 'Valid', SafetyInspection.RESULT_PASSED, 'Van in roadworthy condition.'),
            ('INSP-2026-005', vehicles_map['DL-1L-AA-5544'], today - timedelta(days=15), 'Rajinder Pal', 'Pass', 'Pass', 'Pass', 'Valid', SafetyInspection.RESULT_PASSED, 'Clean safety report for dispatch.'),
            ('INSP-2026-006', vehicles_map['KA-04-HY-9988'], today - timedelta(days=4), 'C. M. Nanjappa', 'Attention Needed', 'Pass', 'Pass', 'Valid', SafetyInspection.RESULT_FAILED, 'Coolant pressure failure detected; declared unsafe for passenger charter.'),
        ]

        for iid, veh, idate, insp_name, brk, tyr, lgt, doc, res, rem in inspections_data:
            SafetyInspection.objects.create(
                inspection_id=iid,
                vehicle=veh,
                inspection_date=idate,
                inspector_name=insp_name,
                brake_condition=brk,
                tyre_condition=tyr,
                lights_condition=lgt,
                documents_verification=doc,
                overall_inspection_result=res,
                remarks=rem
            )
        self.stdout.write(self.style.SUCCESS(f"  Created 6 safety inspections."))

        # 7. Create Fuel Records (14 Consecutive Purchase Records for Mileage Analysis)
        fuel_entries = [
            # Vehicle KA-01-MJ-4512 (Diesel Truck): 3 consecutive records
            (vehicles_map['KA-01-MJ-4512'], Vehicle.FUEL_DIESEL, Decimal('120.00'), Decimal('94.50'), 'Indian Oil Plaza - Electronic City, Bengaluru', today - timedelta(days=20), Decimal('72800.0'), 'INV-IOC-44120'),
            (vehicles_map['KA-01-MJ-4512'], Vehicle.FUEL_DIESEL, Decimal('135.50'), Decimal('94.80'), 'Bharat Petroleum - Tumakuru Highway Hub', today - timedelta(days=12), Decimal('73450.0'), 'INV-BP-55102'),
            (vehicles_map['KA-01-MJ-4512'], Vehicle.FUEL_DIESEL, Decimal('150.00'), Decimal('95.10'), 'HP Auto Care - Hubballi Bypass', today - timedelta(days=4), Decimal('74200.0'), 'INV-HP-99812'),

            # Vehicle KA-05-AB-8910 (Diesel Truck): 3 consecutive records
            (vehicles_map['KA-05-AB-8910'], Vehicle.FUEL_DIESEL, Decimal('140.00'), Decimal('94.20'), 'Indian Oil Hub - Hosur Road, Bengaluru', today - timedelta(days=22), Decimal('95200.0'), 'INV-IOC-88210'),
            (vehicles_map['KA-05-AB-8910'], Vehicle.FUEL_DIESEL, Decimal('145.00'), Decimal('94.60'), 'Reliance Petroleum - Krishnagiri Express Station', today - timedelta(days=14), Decimal('95850.0'), 'INV-REL-11204'),
            (vehicles_map['KA-05-AB-8910'], Vehicle.FUEL_DIESEL, Decimal('130.00'), Decimal('94.90'), 'Bharat Petroleum - Sriperumbudur Depot', today - timedelta(days=2), Decimal('96500.0'), 'INV-BP-33418'),

            # Vehicle MH-12-PQ-3344 (Diesel Truck): 2 records
            (vehicles_map['MH-12-PQ-3344'], Vehicle.FUEL_DIESEL, Decimal('110.00'), Decimal('95.20'), 'Shell Station - Hinjawadi, Pune', today - timedelta(days=16), Decimal('47650.0'), 'INV-SH-44190'),
            (vehicles_map['MH-12-PQ-3344'], Vehicle.FUEL_DIESEL, Decimal('125.00'), Decimal('95.40'), 'Indian Oil Auto Fuel - Panvel, Navi Mumbai', today - timedelta(days=6), Decimal('48300.0'), 'INV-IOC-77123'),

            # Vehicle TN-09-BK-6677 (Diesel Van): 2 records
            (vehicles_map['TN-09-BK-6677'], Vehicle.FUEL_DIESEL, Decimal('45.00'), Decimal('94.10'), 'HP Fuel Station - Guindy, Chennai', today - timedelta(days=15), Decimal('61600.0'), 'INV-HP-11234'),
            (vehicles_map['TN-09-BK-6677'], Vehicle.FUEL_DIESEL, Decimal('48.00'), Decimal('94.30'), 'Bharat Petroleum - Kanchipuram Hub', today - timedelta(days=5), Decimal('62100.0'), 'INV-BP-99021'),

            # Vehicle DL-1L-AA-5544 (Mini Truck): 2 records
            (vehicles_map['DL-1L-AA-5544'], Vehicle.FUEL_DIESEL, Decimal('35.00'), Decimal('93.80'), 'Indian Oil Express - Gurgaon Toll Plaza', today - timedelta(days=18), Decimal('30950.0'), 'INV-IOC-33211'),
            (vehicles_map['DL-1L-AA-5544'], Vehicle.FUEL_DIESEL, Decimal('38.00'), Decimal('94.00'), 'HP Auto Fuel - Neemrana Gateway', today - timedelta(days=3), Decimal('31400.0'), 'INV-HP-44890'),

            # Vehicle KA-51-EX-2020 (Petrol Van): 2 records
            (vehicles_map['KA-51-EX-2020'], Vehicle.FUEL_PETROL, Decimal('40.00'), Decimal('102.50'), 'Shell Petrol Pump - Whitefield, Bengaluru', today - timedelta(days=25), Decimal('28250.0'), 'INV-SH-10293'),
            (vehicles_map['KA-51-EX-2020'], Vehicle.FUEL_PETROL, Decimal('42.00'), Decimal('102.80'), 'Bharat Petroleum - Bannerghatta Road', today - timedelta(days=7), Decimal('28700.0'), 'INV-BP-66512'),
        ]

        fuel_entries.sort(key=lambda x: (x[0].registration_number, x[6]))
        for veh, ftype, qty, price, station, fdate, odo, inv in fuel_entries:
            rec = FuelRecord(
                vehicle=veh,
                fuel_type=ftype,
                fuel_quantity=qty,
                fuel_price_per_litre=price,
                fuel_station=station,
                fuel_date=fdate,
                odometer_reading=odo,
                invoice_number=inv,
                recorded_by=admin_user,
                notes="Authorized company fleet fuel card swipe."
            )
            rec.save()

        self.stdout.write(self.style.SUCCESS(f"  Created 14 fuel purchase records with consecutive mileage calculations."))
        self.stdout.write(self.style.SUCCESS("Demo database successfully populated!"))

Welcome to the Vehicle Rental Management System.
Starting inventory has been loaded (1 Car, 1 Bike, 1 Van).

==================================================
        VEHICLE RENTAL MANAGEMENT SYSTEM
==================================================
 1. View available vehicles
 2. Search vehicles
 3. Register a new customer
 4. Rent a vehicle
 5. Return a vehicle
 6. View a rental invoice
 7. View a customer's rental history
 8. Add a new vehicle (admin)
 9. Exit
==================================================

Enter your choice [1/2/3/4/5/6/7/8/9]: 1

Available Vehicles
--------------------------------------------------
V101 | Car | Toyota Etios | Rs. 2,000 per day
V102 | Bike | Yamaha FZ | Rs. 700 per day
V103 | Van | Tata Winger | Rs. 3,000 per day

Press Enter to return to the menu...3

==================================================
        VEHICLE RENTAL MANAGEMENT SYSTEM
==================================================
 1. View available vehicles
 2. Search vehicles
 3. Register a new customer
 4. Rent a vehicle
 5. Return a vehicle
 6. View a rental invoice
 7. View a customer's rental history
 8. Add a new vehicle (admin)
 9. Exit
==================================================

Enter your choice [1/2/3/4/5/6/7/8/9]: 3

Register a new customer
Enter a customer ID (e.g. C001): C001
Enter full name: JIGYASA
Enter email address: jigyasa@gmail.com
Enter driving licence number: r97897

Customer registered successfully: Customer[C001] JIGYASA <jigyasa@gmail.com>

Press Enter to return to the menu...4

==================================================
        VEHICLE RENTAL MANAGEMENT SYSTEM
==================================================
 1. View available vehicles
 2. Search vehicles
 3. Register a new customer
 4. Rent a vehicle
 5. Return a vehicle
 6. View a rental invoice
 7. View a customer's rental history
 8. Add a new vehicle (admin)
 9. Exit
==================================================

Enter your choice [1/2/3/4/5/6/7/8/9]: 4

Rent a vehicle
Enter your customer ID (or leave blank to register as new): C001

Available Vehicles
--------------------------------------------------
V101 | Car | Toyota Etios | Rs. 2,000 per day
V102 | Bike | Yamaha FZ | Rs. 700 per day
V103 | Van | Tata Winger | Rs. 3,000 per day

Enter the vehicle ID you want to rent: V101
Enter rental duration in days: 3

Choose a payment method:
 1. Card
 2. UPI
Enter choice [1/2]: 2
Enter UPI ID (e.g. name@bank): GFFGHGG@SBI

Rental confirmed!
Rental ID: R0001
Vehicle: Car KA01AB1234
Rental duration: 3 day(s)
Base rental amount: Rs. 6,000.00
Due return date: 2026-08-30
Payment: UPI payment of Rs. 6,000.00 succeeded (ref: G******@SBI, txn: UPI-TXN-0001)

Press Enter to return to the menu...1

==================================================
        VEHICLE RENTAL MANAGEMENT SYSTEM
==================================================
 1. View available vehicles
 2. Search vehicles
 3. Register a new customer
 4. Rent a vehicle
 5. Return a vehicle
 6. View a rental invoice
 7. View a customer's rental history
 8. Add a new vehicle (admin)
 9. Exit
==================================================

Enter your choice [1/2/3/4/5/6/7/8/9]: 1

Available Vehicles
--------------------------------------------------
V102 | Bike | Yamaha FZ | Rs. 700 per day
V103 | Van | Tata Winger | Rs. 3,000 per day

Press Enter to return to the menu...

==================================================
        VEHICLE RENTAL MANAGEMENT SYSTEM
==================================================
 1. View available vehicles
 2. Search vehicles
 3. Register a new customer
 4. Rent a vehicle
 5. Return a vehicle
 6. View a rental invoice
 7. View a customer's rental history
 8. Add a new vehicle (admin)
 9. Exit
==================================================

Enter your choice [1/2/3/4/5/6/7/8/9]: 5

Return a vehicle
Enter the rental ID: R0001
Due return date was: 2026-08-30
How many days late is this return? (0 if on time): 2

Vehicle returned successfully on 2026-09-01.

==================================================
INVOICE INV-R0001
==================================================
Customer        : JIGYASA (C001)
Vehicle         : Car - Toyota Etios (KA01AB1234)
Rental duration : 3 day(s)
Start date      : 2026-08-27
Due return date : 2026-08-30
Actual return   : 2026-09-01
--------------------------------------------------
Base rental amount : Rs. 6,000.00
Late fee           : Rs. 4,800.00
Final amount       : Rs. 10,800.00
Payment            : UPI payment of Rs. 6,000.00 succeeded (ref: G******@SBI, txn: UPI-TXN-0001)
==================================================

Press Enter to return to the menu...

==================================================
        VEHICLE RENTAL MANAGEMENT SYSTEM
==================================================
 1. View available vehicles
 2. Search vehicles
 3. Register a new customer
 4. Rent a vehicle
 5. Return a vehicle
 6. View a rental invoice
 7. View a customer's rental history
 8. Add a new vehicle (admin)
 9. Exit
==================================================

Enter your choice [1/2/3/4/5/6/7/8/9]: 6

View a rental invoice
Enter the rental ID: R0001

==================================================
INVOICE INV-R0001
==================================================
Customer        : JIGYASA (C001)
Vehicle         : Car - Toyota Etios (KA01AB1234)
Rental duration : 3 day(s)
Start date      : 2026-08-27
Due return date : 2026-08-30
Actual return   : 2026-09-01
--------------------------------------------------
Base rental amount : Rs. 6,000.00
Late fee           : Rs. 4,800.00
Final amount       : Rs. 10,800.00
Payment            : UPI payment of Rs. 6,000.00 succeeded (ref: G******@SBI, txn: UPI-TXN-0001)
==================================================

Press Enter to return to the menu...

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

Enter your choice [1/2/3/4/5/6/7/8/9]: 3

Register a new customer
Enter a customer ID (e.g. C001): 123
Enter full name: jigyasa
Enter email address: jigyasa@123
Enter driving licence number: qwr4552

Customer registered successfully: Customer[123] jigyasa <jigyasa@123>

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

Enter your choice [1/2/3/4/5/6/7/8/9]: 4

Rent a vehicle
Enter your customer ID (or leave blank to register as new): 123

Available Vehicles
--------------------------------------------------
V101 | Car | Toyota Etios | Rs. 2,000 per day
V102 | Bike | Yamaha FZ | Rs. 700 per day
V103 | Van | Tata Winger | Rs. 3,000 per day

Enter the vehicle ID you want to rent: V103
Enter rental duration in days: 10

Choose a payment method:
 1. Card
 2. UPI
Enter choice [1/2]: 2
Enter UPI ID (e.g. name@bank): jigyasa@ybl

Rental confirmed!
Rental ID: R0001
Vehicle: Van KA01EF9012
Rental duration: 10 day(s)
Base rental amount: Rs. 30,500.00
Due return date: 2026-09-05
Payment: UPI payment of Rs. 30,500.00 succeeded (ref: j******@ybl, txn: UPI-TXN-0001)

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

Enter your choice [1/2/3/4/5/6/7/8/9]: 2

Search by:
 1. Vehicle ID
 2. Vehicle type (Car / Bike / Van)
 3. Price range
Choose search type [1/2/3]: 2
Enter vehicle type: Van

Found 1 matching vehicle(s):
  V103 | Van | Tata Winger | Rs. 3,000 per day | Rented

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
Due return date was: 2026-09-05
How many days late is this return? (0 if on time): 3

Vehicle returned successfully on 2026-09-08.

==================================================
INVOICE INV-R0001
==================================================
Customer        : jigyasa (123)
Vehicle         : Van - Tata Winger (KA01EF9012)
Rental duration : 10 day(s)
Start date      : 2026-08-26
Due return date : 2026-09-05
Actual return   : 2026-09-08
--------------------------------------------------
Base rental amount : Rs. 30,500.00
Late fee           : Rs. 1,800.00
Final amount       : Rs. 32,300.00
Payment            : UPI payment of Rs. 30,500.00 succeeded (ref: j******@ybl, txn: UPI-TXN-0001)
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
Customer        : jigyasa (123)
Vehicle         : Van - Tata Winger (KA01EF9012)
Rental duration : 10 day(s)
Start date      : 2026-08-26
Due return date : 2026-09-05
Actual return   : 2026-09-08
--------------------------------------------------
Base rental amount : Rs. 30,500.00
Late fee           : Rs. 1,800.00
Final amount       : Rs. 32,300.00
Payment            : UPI payment of Rs. 30,500.00 succeeded (ref: j******@ybl, txn: UPI-TXN-0001)
==================================================

Press Enter to return to the menu...

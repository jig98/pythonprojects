"""
app.py

RentalApp is the terminal front-end. It owns a RentalService (the business
layer) and a simple input/print loop -- it does not contain any business
logic itself (no rate math, no rule checks). Every menu handler:
  1. collects input from the user via console_io helpers
  2. calls into RentalService / models
  3. catches RentalSystemError and prints a friendly message on failure
  4. records what happened via self.logger (ActivityLogger), so every
     operation -- and its outcome -- is saved to data/activity_log.json

This keeps the separation the assignment asks for: RentalService and the
model classes could be reused by a completely different front end (a web
API, a GUI) without any change.
"""

from datetime import timedelta

from cli.activity_log import ActivityLogger
from cli.console_io import prompt_str, prompt_int, prompt_float, prompt_choice, prompt_yes_no, pause
from exceptions import RentalSystemError
from models import Car, Bike, Van, Customer, CardPayment, UpiPayment
from services import RentalService


def _vehicle_summary(vehicle) -> dict:
    return {
        "vehicle_id": vehicle.vehicle_id,
        "type": vehicle.vehicle_type,
        "brand": vehicle.brand,
        "model": vehicle.model,
        "daily_rate": vehicle.daily_rate,
        "is_available": vehicle.is_available,
    }


class RentalApp:
    def __init__(self):
        self.service = RentalService()
        self.logger = ActivityLogger()
        self._seed_initial_data()

    # ---------------------------------------------------------------
    # startup data
    # ---------------------------------------------------------------
    def _seed_initial_data(self):
        """Preload a small starting inventory so the menu isn't empty on first run."""
        self.service.add_vehicle(Car("V101", "KA01AB1234", "Toyota", "Etios", 2000))
        self.service.add_vehicle(Bike("V102", "KA01CD5678", "Yamaha", "FZ", 700))
        self.service.add_vehicle(Van("V103", "KA01EF9012", "Tata", "Winger", 3000, service_charge=500))

    # ---------------------------------------------------------------
    # main loop
    # ---------------------------------------------------------------
    MENU_TEXT = """
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
"""

    HANDLERS = None       # populated at the bottom of the class
    ACTION_NAMES = {       # menu choice -> action name used in the activity log
        "1": "view_available_vehicles",
        "2": "search_vehicles",
        "3": "register_customer",
        "4": "rent_vehicle",
        "5": "return_vehicle",
        "6": "view_invoice",
        "7": "view_rental_history",
        "8": "add_vehicle",
    }

    def run(self):
        print("Welcome to the Vehicle Rental Management System.")
        print("Starting inventory has been loaded (1 Car, 1 Bike, 1 Van).")
        print(f"Every action you take is saved to: {self.logger.path}")
        while True:
            print(self.MENU_TEXT)
            choice = prompt_choice("Enter your choice", [str(i) for i in range(1, 10)])
            if choice == "9":
                print("\nThank you for using the Vehicle Rental Management System. Goodbye!")
                break
            handler = self.HANDLERS[choice]
            try:
                handler(self)
            except RentalSystemError as e:
                print(f"\n[Error] {e}")
                self.logger.log(
                    action=self.ACTION_NAMES.get(choice, "unknown"),
                    status="error",
                    details={"error_type": type(e).__name__, "message": str(e)},
                )
            pause()

    # ---------------------------------------------------------------
    # 1. view available vehicles
    # ---------------------------------------------------------------
    def handle_view_available(self):
        print()
        self.service.display_available_vehicles()

        available = [v for v in self.service.list_all_vehicles() if v.is_available]
        self.logger.log(
            action="view_available_vehicles",
            status="success",
            details={"count": len(available), "vehicles": [_vehicle_summary(v) for v in available]},
        )

    # ---------------------------------------------------------------
    # 2. search vehicles
    # ---------------------------------------------------------------
    def handle_search(self):
        print("\nSearch by:")
        print(" 1. Vehicle ID")
        print(" 2. Vehicle type (Car / Bike / Van)")
        print(" 3. Price range")
        mode = prompt_choice("Choose search type", ["1", "2", "3"])

        if mode == "1":
            vehicle_id = prompt_str("Enter vehicle ID")
            results = self.service.search_vehicles(vehicle_id=vehicle_id)
            criteria = {"mode": "vehicle_id", "vehicle_id": vehicle_id}
        elif mode == "2":
            vehicle_type = prompt_str("Enter vehicle type")
            results = self.service.search_vehicles(vehicle_type=vehicle_type)
            criteria = {"mode": "vehicle_type", "vehicle_type": vehicle_type}
        else:
            min_price = prompt_float("Enter minimum daily rate", min_value=0)
            max_price = prompt_float("Enter maximum daily rate", min_value=min_price)
            results = self.service.search_vehicles(min_price=min_price, max_price=max_price)
            criteria = {"mode": "price_range", "min_price": min_price, "max_price": max_price}

        print()
        if not results:
            print("No matching vehicles found.")
        else:
            print(f"Found {len(results)} matching vehicle(s):")
            for v in results:
                print(f"  {v.display_details()}")

        self.logger.log(
            action="search_vehicles",
            status="success",
            details={
                "criteria": criteria,
                "result_count": len(results),
                "results": [_vehicle_summary(v) for v in results],
            },
        )

    # ---------------------------------------------------------------
    # 3. register a new customer
    # ---------------------------------------------------------------
    def handle_register_customer(self):
        print("\nRegister a new customer")
        customer_id = prompt_str("Enter a customer ID (e.g. C001)")
        if self.service.get_customer(customer_id):
            print(f"  A customer with ID {customer_id} already exists.")
            self.logger.log(
                action="register_customer",
                status="blocked",
                details={"reason": "duplicate_customer_id", "customer_id": customer_id},
            )
            return
        name = prompt_str("Enter full name")
        email = prompt_str("Enter email address")
        licence_number = prompt_str("Enter driving licence number")

        customer = Customer(customer_id, name, email, licence_number)
        self.service.register_customer(customer)
        print(f"\nCustomer registered successfully: {customer}")

        self.logger.log(
            action="register_customer",
            status="success",
            details={
                "customer_id": customer_id, "name": name,
                "email": email, "licence_number": licence_number,
            },
        )

    # ---------------------------------------------------------------
    # 4. rent a vehicle
    # ---------------------------------------------------------------
    def handle_rent_vehicle(self):
        print("\nRent a vehicle")
        customer = self._get_or_register_customer()
        if customer is None:
            return

        print()
        self.service.display_available_vehicles()
        vehicle_id = prompt_str("\nEnter the vehicle ID you want to rent")

        # Fail fast on a missing/unavailable vehicle before asking for payment details.
        matches = self.service.search_vehicles(vehicle_id=vehicle_id)
        if not matches:
            print(f"  No vehicle found with ID {vehicle_id}.")
            self.logger.log(
                action="rent_vehicle", status="blocked",
                details={"reason": "vehicle_not_found", "vehicle_id": vehicle_id, "customer_id": customer.customer_id},
            )
            return
        if not matches[0].is_available:
            print(f"  Vehicle {vehicle_id} ({matches[0].vehicle_type}) is currently unavailable.")
            self.logger.log(
                action="rent_vehicle", status="blocked",
                details={
                    "reason": "vehicle_unavailable", "vehicle_id": vehicle_id,
                    "vehicle_type": matches[0].vehicle_type, "customer_id": customer.customer_id,
                },
            )
            return

        days = prompt_int("Enter rental duration in days", min_value=1)
        payment_processor = self._collect_payment_method()

        rental = self.service.rent_vehicle(customer, vehicle_id, days, payment_processor)

        print(f"\nRental confirmed!")
        print(f"Rental ID: {rental.rental_id}")
        print(f"Vehicle: {rental.vehicle.vehicle_type} {rental.vehicle.registration_number}")
        print(f"Rental duration: {rental.rental_days} day(s)")
        print(f"Base rental amount: Rs. {rental.base_amount:,.2f}")
        print(f"Due return date: {rental.due_return_date}")
        print(f"Payment: {rental.payment_result}")

        self.logger.log(
            action="rent_vehicle",
            status="success",
            details={
                "rental_id": rental.rental_id,
                "customer_id": customer.customer_id,
                "customer_name": customer.name,
                "vehicle_id": rental.vehicle.vehicle_id,
                "vehicle_type": rental.vehicle.vehicle_type,
                "rental_days": rental.rental_days,
                "base_amount": rental.base_amount,
                "due_return_date": rental.due_return_date,
                "payment_method": rental.payment_result.method,
                "payment_reference": rental.payment_result.masked_reference,
                "transaction_id": rental.payment_result.transaction_id,
            },
        )

    # ---------------------------------------------------------------
    # 5. return a vehicle
    # ---------------------------------------------------------------
    def handle_return_vehicle(self):
        print("\nReturn a vehicle")
        rental_id = prompt_str("Enter the rental ID")
        rental = self.service.get_rental(rental_id)

        if rental.status == "RETURNED":
            print(f"  Rental {rental_id} has already been returned.")
            self.logger.log(
                action="return_vehicle", status="blocked",
                details={"reason": "already_returned", "rental_id": rental_id},
            )
            return

        print(f"Due return date was: {rental.due_return_date}")
        late_days = prompt_int("How many days late is this return? (0 if on time)", min_value=0)
        return_date = rental.due_return_date + timedelta(days=late_days)

        invoice = self.service.return_vehicle(rental_id, return_date)

        print(f"\nVehicle returned successfully on {return_date}.")
        print()
        invoice.display()

        self.logger.log(
            action="return_vehicle",
            status="success",
            details={
                "rental_id": rental_id,
                "vehicle_id": rental.vehicle.vehicle_id,
                "customer_id": rental.customer.customer_id,
                "return_date": return_date,
                "late_days": late_days,
                "base_amount": rental.base_amount,
                "late_fee": rental.late_fee,
                "total_amount": rental.total_amount,
            },
        )

    # ---------------------------------------------------------------
    # 6. view invoice
    # ---------------------------------------------------------------
    def handle_view_invoice(self):
        print("\nView a rental invoice")
        rental_id = prompt_str("Enter the rental ID")
        invoice = self.service.get_invoice(rental_id)
        print()
        invoice.display()

        rental = self.service.get_rental(rental_id)
        self.logger.log(
            action="view_invoice",
            status="success",
            details={
                "rental_id": rental_id,
                "base_amount": rental.base_amount,
                "late_fee": rental.late_fee,
                "total_amount": rental.total_amount,
            },
        )

    # ---------------------------------------------------------------
    # 7. view rental history
    # ---------------------------------------------------------------
    def handle_view_history(self):
        print("\nView a customer's rental history")
        customer_id = prompt_str("Enter the customer ID")
        customer = self.service.get_customer(customer_id)
        if not customer:
            print(f"  No customer found with ID {customer_id}.")
            self.logger.log(
                action="view_rental_history", status="blocked",
                details={"reason": "customer_not_found", "customer_id": customer_id},
            )
            return
        print()
        print(customer.display_rental_history())

        rentals = customer.rental_history
        self.logger.log(
            action="view_rental_history",
            status="success",
            details={
                "customer_id": customer_id,
                "rental_count": len(rentals),
                "rentals": [
                    {
                        "rental_id": r.rental_id,
                        "vehicle_type": r.vehicle.vehicle_type,
                        "vehicle_id": r.vehicle.vehicle_id,
                        "status": r.status,
                        "total_amount": r.total_amount,
                    }
                    for r in rentals
                ],
            },
        )

    # ---------------------------------------------------------------
    # 8. add a new vehicle (admin)
    # ---------------------------------------------------------------
    def handle_add_vehicle(self):
        print("\nAdd a new vehicle")
        vehicle_id = prompt_str("Enter a vehicle ID (e.g. V104)")
        vehicle_type = prompt_choice("Vehicle type", ["Car", "Bike", "Van"])
        registration_number = prompt_str("Enter registration number")
        brand = prompt_str("Enter brand")
        model = prompt_str("Enter model")
        daily_rate = prompt_float("Enter daily rental rate", min_value=0.01)

        service_charge = None
        if vehicle_type == "Car":
            vehicle = Car(vehicle_id, registration_number, brand, model, daily_rate)
        elif vehicle_type == "Bike":
            vehicle = Bike(vehicle_id, registration_number, brand, model, daily_rate)
        else:
            service_charge = prompt_float("Enter service charge", min_value=0)
            vehicle = Van(vehicle_id, registration_number, brand, model, daily_rate, service_charge)

        self.service.add_vehicle(vehicle)
        print(f"\nVehicle added successfully: {vehicle.display_details()}")

        details = {
            "vehicle_id": vehicle_id, "type": vehicle_type,
            "registration_number": registration_number, "brand": brand,
            "model": model, "daily_rate": daily_rate,
        }
        if service_charge is not None:
            details["service_charge"] = service_charge
        self.logger.log(action="add_vehicle", status="success", details=details)

    # ---------------------------------------------------------------
    # shared helpers
    # ---------------------------------------------------------------
    def _get_or_register_customer(self):
        customer_id = prompt_str("Enter your customer ID (or leave blank to register as new)",
                                  allow_empty=True)
        if not customer_id:
            print("\nLet's register you as a new customer first.")
            self.handle_register_customer()
            customer_id = prompt_str("Now enter the customer ID you just created")

        customer = self.service.get_customer(customer_id)
        if not customer:
            print(f"  No customer found with ID {customer_id}.")
            if prompt_yes_no("Would you like to register a new customer instead?"):
                self.handle_register_customer()
                return None
            return None
        return customer

    def _collect_payment_method(self):
        print("\nChoose a payment method:")
        print(" 1. Card")
        print(" 2. UPI")
        method = prompt_choice("Enter choice", ["1", "2"])

        if method == "1":
            card_number = prompt_str("Enter card number")
            card_holder_name = prompt_str("Enter name on card")
            return CardPayment(card_number, card_holder_name)
        else:
            upi_id = prompt_str("Enter UPI ID (e.g. name@bank)")
            return UpiPayment(upi_id)

    HANDLERS = {
        "1": handle_view_available,
        "2": handle_search,
        "3": handle_register_customer,
        "4": handle_rent_vehicle,
        "5": handle_return_vehicle,
        "6": handle_view_invoice,
        "7": handle_view_history,
        "8": handle_add_vehicle,
    }

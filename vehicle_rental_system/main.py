"""
main.py

Runs the mandatory demonstration scenario from the assignment, step by step,
with the step number printed before each action so the console output can
be matched directly back to the assignment's checklist.
"""

from datetime import date, timedelta

from models import Car, Bike, Van, Customer, CardPayment, UpiPayment
from services import RentalService
from exceptions import VehicleUnavailableError, PaymentFailedError, RentalSystemError


def step(n, text):
    print(f"\n[Step {n}] {text}")


def main():
    service = RentalService()

    # ---- Step 1: Add one car, one bike, and one van ----
    step(1, "Adding vehicles (1 car, 1 bike, 1 van)")
    car = Car("V101", "KA01AB1234", "Toyota", "Etios", 2000)
    bike = Bike("V102", "KA01CD5678", "Yamaha", "FZ", 700)
    van = Van("V103", "KA01EF9012", "Tata", "Winger", 3000, service_charge=500)
    service.add_vehicle(car)
    service.add_vehicle(bike)
    service.add_vehicle(van)
    print("Vehicles added successfully.")

    # ---- Step 2: Register two customers ----
    step(2, "Registering two customers")
    customer_a = Customer("C001", "Ananya Sharma", "ananya@example.com", "DL-1420110012345")
    customer_b = Customer("C002", "Rohit Verma", "rohit@example.com", "DL-1420110054321")
    service.register_customer(customer_a)
    service.register_customer(customer_b)
    print(f"Registered: {customer_a}")
    print(f"Registered: {customer_b}")

    # ---- Step 3: Display all available vehicles ----
    step(3, "Displaying all available vehicles")
    service.display_available_vehicles()

    # ---- Step 4: Customer A rents the car for three days ----
    step(4, "Customer A rents the car (V101) for 3 days")
    card_payment = CardPayment("4111 1111 1111 1234", "Ananya Sharma")
    rental_a = service.rent_vehicle(customer_a, "V101", 3, card_payment)
    print(f"Selected vehicle: {rental_a.vehicle.vehicle_id}")
    print(f"Rental duration: {rental_a.rental_days} days")
    print(f"Base rental amount: Rs. {rental_a.base_amount:,.0f}")
    print(f"Payment completed successfully. ({rental_a.payment_result})")

    # ---- Step 5: Attempt to rent the same car to Customer B ----
    step(5, "Attempting to rent the same car (V101) to Customer B")
    upi_payment = UpiPayment("rohit@upi")
    try:
        service.rent_vehicle(customer_b, "V101", 2, upi_payment)
    except VehicleUnavailableError as e:
        # ---- Step 6: Display an appropriate 'Vehicle unavailable' message ----
        step(6, "Expected failure caught")
        print(f"Error: {e}")

    # ---- Step 7: Process Customer A's payment successfully ----
    # (Payment for the rental was already required to succeed in Step 4
    #  before the rental was confirmed -- re-stated here for clarity.)
    step(7, "Confirming Customer A's payment was processed successfully")
    print("Payment completed successfully.")

    # ---- Step 8: Return the car one day late ----
    step(8, "Returning the car (V101) one day late")
    return_date = rental_a.due_return_date + timedelta(days=1)
    invoice = service.return_vehicle(rental_a.rental_id, return_date)
    print(f"Vehicle returned successfully on {return_date}.")

    # ---- Step 9: Calculate base amount, late fee, final amount ----
    step(9, "Rental cost breakdown")
    print(f"Base rental amount: Rs. {rental_a.base_amount:,.0f}")
    print(f"Late fee: Rs. {rental_a.late_fee:,.0f}")
    print(f"Final amount: Rs. {rental_a.total_amount:,.0f}")

    # ---- Step 10: Display the final invoice ----
    step(10, "Final invoice")
    invoice.display()

    # ---- Step 11: Confirm that the returned car is available again ----
    step(11, "Confirming the car is available again")
    print(f"Vehicle {car.vehicle_id} available: {car.is_available}")

    # ---- Step 12: Display Customer A's rental history ----
    step(12, "Customer A's rental history")
    print(customer_a.display_rental_history())


if __name__ == "__main__":
    main()

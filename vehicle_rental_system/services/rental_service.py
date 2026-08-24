"""
rental_service.py

RentalService owns the business workflow: searching vehicles, renting,
returning, and invoicing. It depends on the PaymentProcessor *interface*
only (dependency inversion) -- it has no idea whether it was handed a
CardPayment or a UpiPayment, and does not need to.

Method overloading note: Python has no native method-overloading syntax
(no two defs with the same name but different parameter lists coexist --
the second simply replaces the first). The idiomatic Python way to offer
"search by ID, or by type, or by price range" is a single entry point with
optional keyword parameters, which is what search_vehicles() below does.
The three private helpers (_search_by_id / _search_by_type /
_search_by_price_range) show the distinct behaviours that, in a language
like Java or C#, would be written as genuinely overloaded methods.
"""

from datetime import date

from exceptions import (
    VehicleUnavailableError,
    VehicleNotFoundError,
    RentalNotFoundError,
    InvalidRentalDurationError,
    PaymentFailedError,
)
from models import Rental, Invoice, PaymentProcessor


class RentalService:
    def __init__(self):
        self.__vehicles = {}     # vehicle_id -> Vehicle
        self.__customers = {}    # customer_id -> Customer
        self.__rentals = {}      # rental_id -> Rental
        self.__rental_counter = 0

    # ---------------- vehicle & customer registration ----------------
    def add_vehicle(self, vehicle) -> None:
        self.__vehicles[vehicle.vehicle_id] = vehicle

    def register_customer(self, customer) -> None:
        self.__customers[customer.customer_id] = customer

    # ---------------- search (overload-style dispatch) ----------------
    def search_vehicles(self, vehicle_id: str = None, vehicle_type: str = None,
                         min_price: float = None, max_price: float = None):
        if vehicle_id is not None:
            return self._search_by_id(vehicle_id)
        if vehicle_type is not None:
            return self._search_by_type(vehicle_type)
        if min_price is not None or max_price is not None:
            return self._search_by_price_range(min_price or 0, max_price or float("inf"))
        return list(self.__vehicles.values())

    def _search_by_id(self, vehicle_id: str):
        vehicle = self.__vehicles.get(vehicle_id)
        return [vehicle] if vehicle else []

    def _search_by_type(self, vehicle_type: str):
        return [v for v in self.__vehicles.values()
                if v.vehicle_type.lower() == vehicle_type.lower()]

    def _search_by_price_range(self, min_price: float, max_price: float):
        return [v for v in self.__vehicles.values()
                if min_price <= v.daily_rate <= max_price]

    def display_available_vehicles(self) -> None:
        available = [v for v in self.__vehicles.values() if v.is_available]
        print("Available Vehicles")
        print("-" * 50)
        if not available:
            print("No vehicles currently available.")
        for v in available:
            print(f"{v.vehicle_id} | {v.vehicle_type} | {v.brand} {v.model} | "
                  f"Rs. {v.daily_rate:,.0f} per day")

    # ---------------- rental workflow ----------------
    def rent_vehicle(self, customer, vehicle_id: str, days: int,
                      payment_processor: PaymentProcessor) -> Rental:
        """
        Steps mirror the assignment's rental workflow:
        1. locate the vehicle          2. confirm availability
        3. validate duration            4. process payment BEFORE confirming
        5. mark unavailable & create the rental record
        """
        matches = self._search_by_id(vehicle_id)
        if not matches:
            raise VehicleNotFoundError(f"No vehicle found with ID {vehicle_id}.")
        vehicle = matches[0]

        if not vehicle.is_available:
            raise VehicleUnavailableError(
                f"Vehicle {vehicle.vehicle_id} ({vehicle.vehicle_type}) is currently unavailable."
            )
        if not isinstance(days, int) or days <= 0:
            raise InvalidRentalDurationError("Rental duration must be a positive whole number of days.")

        # Pre-compute what the customer owes so payment matches the rental.
        provisional_amount = vehicle.calculate_rental_cost(days)

        # Payment MUST succeed before we touch vehicle/rental state.
        try:
            payment_result = payment_processor.process_payment(provisional_amount)
        except PaymentFailedError:
            raise  # re-raise; rental is never created if payment fails

        self.__rental_counter += 1
        rental_id = f"R{self.__rental_counter:04d}"
        rental = Rental(rental_id, customer, vehicle, days)
        rental.attach_payment(payment_result)

        vehicle.mark_as_rented()
        customer.add_rental(rental)
        self.__rentals[rental_id] = rental

        return rental

    def return_vehicle(self, rental_id: str, return_date: date = None) -> Invoice:
        rental = self.__rentals.get(rental_id)
        if not rental:
            raise RentalNotFoundError(f"No active rental found with ID {rental_id}.")

        rental.complete_rental(return_date or date.today())
        invoice = Invoice(rental)
        invoice.generate()
        return invoice

    def get_rental(self, rental_id: str) -> Rental:
        rental = self.__rentals.get(rental_id)
        if not rental:
            raise RentalNotFoundError(f"No rental found with ID {rental_id}.")
        return rental

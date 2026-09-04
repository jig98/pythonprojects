"""
rental.py

A Rental is composed of a Customer, a Vehicle, and (once payment succeeds)
a PaymentResult -- if the Rental is destroyed, those particular details of
that transaction go with it (composition), while the Customer and Vehicle
objects themselves live on independently and are only *associated* with
this Rental.
"""

from datetime import date, timedelta

from exceptions import InvalidRentalDurationError

LATE_FEE_RATE = 0.20  # 20% of daily rate, per late day


class Rental:
    def __init__(self, rental_id: str, customer, vehicle, rental_days: int,
                 start_date: date = None):
        if not isinstance(rental_days, int) or rental_days <= 0:
            raise InvalidRentalDurationError("Rental days must be a whole number greater than zero.")

        self.__rental_id = rental_id
        self.__customer = customer
        self.__vehicle = vehicle
        self.__rental_days = rental_days
        self.__start_date = start_date or date.today()
        self.__due_return_date = self.__start_date + timedelta(days=rental_days)
        self.__actual_return_date = None
        self.__status = "CONFIRMED"  # CONFIRMED -> RETURNED
        self.__payment_result = None
        self.__base_amount = vehicle.calculate_rental_cost(rental_days)
        self.__late_fee = 0.0
        self.__total_amount = self.__base_amount

    # ---- read-only properties ----
    @property
    def rental_id(self):
        return self.__rental_id

    @property
    def customer(self):
        return self.__customer

    @property
    def vehicle(self):
        return self.__vehicle

    @property
    def rental_days(self):
        return self.__rental_days

    @property
    def start_date(self):
        return self.__start_date

    @property
    def due_return_date(self):
        return self.__due_return_date

    @property
    def actual_return_date(self):
        return self.__actual_return_date

    @property
    def status(self):
        return self.__status

    @property
    def base_amount(self):
        return self.__base_amount

    @property
    def late_fee(self):
        return self.__late_fee

    @property
    def total_amount(self):
        return self.__total_amount

    @property
    def payment_result(self):
        return self.__payment_result

    def attach_payment(self, payment_result) -> None:
        """Called by RentalService only after PaymentProcessor confirms success."""
        self.__payment_result = payment_result

    def calculate_late_days(self, return_date: date) -> int:
        late_days = (return_date - self.__due_return_date).days
        return max(late_days, 0)

    def calculate_final_amount(self, return_date: date) -> float:
        late_days = self.calculate_late_days(return_date)
        self.__late_fee = late_days * LATE_FEE_RATE * self.__vehicle.daily_rate
        self.__total_amount = self.__base_amount + self.__late_fee
        return self.__total_amount

    def complete_rental(self, return_date: date = None) -> None:
        return_date = return_date or date.today()
        self.__actual_return_date = return_date
        self.calculate_final_amount(return_date)
        self.__status = "RETURNED"
        self.__vehicle.mark_as_available()

    def __str__(self):
        return (f"Rental[{self.__rental_id}] {self.__customer.name} -> "
                f"{self.__vehicle.vehicle_type} {self.__vehicle.registration_number} "
                f"({self.__rental_days}d) [{self.__status}]")

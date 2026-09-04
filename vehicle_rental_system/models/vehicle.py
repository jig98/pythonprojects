"""
vehicle.py

Vehicle is an abstract base class: it defines *what* every rentable thing
in this system must be able to do (calculate_rental_cost, display_details,
mark_as_rented, mark_as_available) without dictating *how* the cost is
calculated. Car, Bike, and Van each provide their own calculate_rental_cost
implementation. This is the polymorphism the assignment asks for: calling
code (RentalService) always calls vehicle.calculate_rental_cost(days) and
never has to ask "what type of vehicle is this?" with an if/elif chain.
"""

from abc import ABC, abstractmethod

from exceptions import ValidationError


class Vehicle(ABC):
    """
    Abstract base class for every rentable vehicle.

    All fields are stored as private attributes (name-mangled with a double
    leading underscore) and exposed only through read-only properties, so
    external code cannot silently corrupt a vehicle's state (encapsulation).
    """

    def __init__(self, vehicle_id: str, registration_number: str,
                 brand: str, model: str, daily_rate: float):
        if not vehicle_id or not str(vehicle_id).strip():
            raise ValidationError("Vehicle ID cannot be empty.")
        if not registration_number or not registration_number.strip():
            raise ValidationError("A vehicle must have a valid registration number.")
        if not brand or not brand.strip():
            raise ValidationError("Brand cannot be empty.")
        if not model or not model.strip():
            raise ValidationError("Model cannot be empty.")
        if daily_rate is None or daily_rate <= 0:
            raise ValidationError("Daily rental rate must be a positive number.")

        self.__vehicle_id = vehicle_id
        self.__registration_number = registration_number
        self.__brand = brand
        self.__model = model
        self.__daily_rate = float(daily_rate)
        self.__available = True

    # ---- read-only access to private state (encapsulation) ----
    @property
    def vehicle_id(self) -> str:
        return self.__vehicle_id

    @property
    def registration_number(self) -> str:
        return self.__registration_number

    @property
    def brand(self) -> str:
        return self.__brand

    @property
    def model(self) -> str:
        return self.__model

    @property
    def daily_rate(self) -> float:
        return self.__daily_rate

    @property
    def is_available(self) -> bool:
        return self.__available

    @property
    def vehicle_type(self) -> str:
        """Returns the concrete subclass name, e.g. 'Car', 'Bike', 'Van'."""
        return type(self).__name__

    # ---- controlled state transitions ----
    def mark_as_rented(self) -> None:
        if not self.__available:
            raise ValidationError(f"Vehicle {self.__vehicle_id} is already rented.")
        self.__available = False

    def mark_as_available(self) -> None:
        self.__available = True

    # ---- abstraction: subclasses MUST supply their own pricing rule ----
    @abstractmethod
    def calculate_rental_cost(self, days: int) -> float:
        """Return the base rental cost for the given number of days."""
        raise NotImplementedError

    def display_details(self) -> str:
        status = "Available" if self.__available else "Rented"
        return (f"{self.__vehicle_id} | {self.vehicle_type} | {self.__brand} "
                f"{self.__model} | Rs. {self.__daily_rate:,.0f} per day | {status}")

    def __str__(self) -> str:
        return self.display_details()


class Car(Vehicle):
    """Car cost = daily rate x rental days. No special adjustment."""

    def calculate_rental_cost(self, days: int) -> float:
        return self.daily_rate * days


class Bike(Vehicle):
    """Bike cost = daily rate x days, with a 5% discount for rentals over 5 days."""

    LONG_RENTAL_THRESHOLD_DAYS = 5
    LONG_RENTAL_DISCOUNT = 0.05

    def calculate_rental_cost(self, days: int) -> float:
        base_cost = self.daily_rate * days
        if days > self.LONG_RENTAL_THRESHOLD_DAYS:
            return base_cost * (1 - self.LONG_RENTAL_DISCOUNT)
        return base_cost


class Van(Vehicle):
    """Van cost = (daily rate x days) + a flat service charge."""

    def __init__(self, vehicle_id: str, registration_number: str,
                 brand: str, model: str, daily_rate: float,
                 service_charge: float = 500.0):
        super().__init__(vehicle_id, registration_number, brand, model, daily_rate)
        if service_charge < 0:
            raise ValidationError("Service charge cannot be negative.")
        self.__service_charge = float(service_charge)

    @property
    def service_charge(self) -> float:
        return self.__service_charge

    def calculate_rental_cost(self, days: int) -> float:
        return (self.daily_rate * days) + self.__service_charge

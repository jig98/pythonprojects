"""
customer.py

Customer stores identity details and an association to every Rental the
customer has ever made (a Customer can have many Rentals over time).
"""

from exceptions import ValidationError


class Customer:
    def __init__(self, customer_id: str, name: str, email: str, licence_number: str):
        if not customer_id or not str(customer_id).strip():
            raise ValidationError("Customer ID cannot be empty.")
        if not name or not name.strip():
            raise ValidationError("Customer name cannot be empty.")
        if not email or "@" not in email:
            raise ValidationError("A valid email address is required.")
        if not licence_number or not licence_number.strip():
            raise ValidationError("Driving licence number cannot be empty.")

        self.__customer_id = customer_id
        self.__name = name
        self.__email = email
        self.__licence_number = licence_number
        self.__rental_history = []  # list[Rental] -- association, populated over time

    @property
    def customer_id(self) -> str:
        return self.__customer_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def email(self) -> str:
        return self.__email

    @property
    def licence_number(self) -> str:
        return self.__licence_number

    @property
    def rental_history(self) -> list:
        # return a copy so external code cannot mutate internal state directly
        return list(self.__rental_history)

    def add_rental(self, rental) -> None:
        self.__rental_history.append(rental)

    def display_rental_history(self) -> str:
        if not self.__rental_history:
            return f"{self.__name} has no rental history yet."

        lines = [f"Rental history for {self.__name} ({self.__customer_id}):"]
        for rental in self.__rental_history:
            lines.append(
                f"  - {rental.rental_id}: {rental.vehicle.vehicle_type} "
                f"{rental.vehicle.registration_number} | {rental.rental_days} day(s) "
                f"| Status: {rental.status} | Total: Rs. {rental.total_amount:,.2f}"
            )
        return "\n".join(lines)

    def __str__(self) -> str:
        return f"Customer[{self.__customer_id}] {self.__name} <{self.__email}>"

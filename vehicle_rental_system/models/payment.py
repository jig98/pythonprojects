"""
payment.py

PaymentProcessor is the contract (interface) the rest of the system depends
on. RentalService never imports CardPayment or UpiPayment directly when
processing a rental -- it is handed *some* PaymentProcessor and calls
process_payment(amount) on it. This is dependency inversion: swap in a new
payment method (e.g. NetBankingPayment) tomorrow and RentalService does not
change at all.

Sensitive details (card number, UPI id) are masked immediately in __init__
and the raw value is never stored or printed, satisfying the "sensitive
payment information must not be stored as plain text" business rule.
"""

from abc import ABC, abstractmethod

from exceptions import ValidationError, PaymentFailedError


class PaymentProcessor(ABC):
    """Interface every concrete payment method must implement."""

    @abstractmethod
    def process_payment(self, amount: float) -> "PaymentResult":
        raise NotImplementedError


class PaymentResult:
    """Simple value object returned by a successful payment."""

    def __init__(self, method: str, masked_reference: str, amount: float, transaction_id: str):
        self.method = method
        self.masked_reference = masked_reference
        self.amount = amount
        self.transaction_id = transaction_id

    def __str__(self):
        return (f"{self.method} payment of Rs. {self.amount:,.2f} succeeded "
                f"(ref: {self.masked_reference}, txn: {self.transaction_id})")


class CardPayment(PaymentProcessor):
    def __init__(self, card_number: str, card_holder_name: str):
        if not card_number or len(card_number.replace(" ", "")) < 12:
            raise ValidationError("A valid card number is required.")
        if not card_holder_name or not card_holder_name.strip():
            raise ValidationError("Card holder name cannot be empty.")
        digits = card_number.replace(" ", "")
        # Store only a masked reference -- never the full card number.
        self.__masked_number = f"**** **** **** {digits[-4:]}"
        self.__card_holder_name = card_holder_name
        self.__transaction_counter = 0

    def process_payment(self, amount: float) -> PaymentResult:
        if amount <= 0:
            raise PaymentFailedError("Payment amount must be greater than zero.")
        self.__transaction_counter += 1
        txn_id = f"CARD-TXN-{self.__transaction_counter:04d}"
        return PaymentResult("Card", self.__masked_number, amount, txn_id)


class UpiPayment(PaymentProcessor):
    def __init__(self, upi_id: str):
        if not upi_id or "@" not in upi_id:
            raise ValidationError("A valid UPI ID is required (e.g. name@bank).")
        handle, _, provider = upi_id.partition("@")
        masked_handle = handle[0] + "*" * max(len(handle) - 1, 1)
        self.__masked_upi = f"{masked_handle}@{provider}"
        self.__transaction_counter = 0

    def process_payment(self, amount: float) -> PaymentResult:
        if amount <= 0:
            raise PaymentFailedError("Payment amount must be greater than zero.")
        self.__transaction_counter += 1
        txn_id = f"UPI-TXN-{self.__transaction_counter:04d}"
        return PaymentResult("UPI", self.__masked_upi, amount, txn_id)

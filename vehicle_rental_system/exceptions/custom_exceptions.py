"""
custom_exceptions.py

All exceptions raised by the Vehicle Rental Management System inherit from
RentalSystemError so calling code can catch the whole family with one
except clause, or catch a specific failure (e.g. PaymentFailedError) when
it needs to react differently.
"""


class RentalSystemError(Exception):
    """Base class for every exception raised by this application."""
    pass


class ValidationError(RentalSystemError):
    """Raised when a required field is empty or otherwise invalid."""
    pass


class InvalidRentalDurationError(RentalSystemError):
    """Raised when rental days is not a positive whole number."""
    pass


class VehicleUnavailableError(RentalSystemError):
    """Raised when a customer tries to rent a vehicle that is not available."""
    pass


class VehicleNotFoundError(RentalSystemError):
    """Raised when a search/lookup does not match any vehicle."""
    pass


class PaymentFailedError(RentalSystemError):
    """Raised when a PaymentProcessor implementation cannot complete a payment."""
    pass


class RentalNotFoundError(RentalSystemError):
    """Raised when a rental id does not match any active rental record."""
    pass

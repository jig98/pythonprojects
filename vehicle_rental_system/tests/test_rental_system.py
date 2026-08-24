"""
test_rental_system.py

Run with:  python -m unittest tests.test_rental_system -v
(from the vehicle_rental_system folder)

Covers both success paths (rentals/returns that should work) and failure
paths (validation errors, unavailable vehicle, invalid duration, payment
failure) as required by the assignment.
"""

import unittest
from datetime import date, timedelta

from models import Car, Bike, Van, Customer, CardPayment, UpiPayment, PaymentProcessor
from models.payment import PaymentResult
from services import RentalService
from exceptions import (
    ValidationError,
    InvalidRentalDurationError,
    VehicleUnavailableError,
    VehicleNotFoundError,
    PaymentFailedError,
    RentalNotFoundError,
)


class AlwaysFailsPayment(PaymentProcessor):
    """Test double used to prove the system handles payment failure correctly."""
    def process_payment(self, amount):
        raise PaymentFailedError("Simulated gateway timeout.")


class TestVehiclePolymorphism(unittest.TestCase):
    def test_car_cost_is_linear(self):
        car = Car("V1", "KA01AA0001", "Toyota", "Etios", 2000)
        self.assertEqual(car.calculate_rental_cost(3), 6000)

    def test_bike_no_discount_at_or_under_five_days(self):
        bike = Bike("V2", "KA01AA0002", "Yamaha", "FZ", 700)
        self.assertEqual(bike.calculate_rental_cost(5), 3500)

    def test_bike_discount_over_five_days(self):
        bike = Bike("V2", "KA01AA0002", "Yamaha", "FZ", 700)
        expected = (700 * 6) * 0.95
        self.assertEqual(bike.calculate_rental_cost(6), expected)

    def test_van_adds_service_charge(self):
        van = Van("V3", "KA01AA0003", "Tata", "Winger", 3000, service_charge=500)
        self.assertEqual(van.calculate_rental_cost(2), 3000 * 2 + 500)

    def test_polymorphic_dispatch_through_base_reference(self):
        """Same call, different behaviour per subclass -- no type-checking needed."""
        vehicles = [
            Car("V1", "KA01AA0001", "Toyota", "Etios", 2000),
            Bike("V2", "KA01AA0002", "Yamaha", "FZ", 700),
            Van("V3", "KA01AA0003", "Tata", "Winger", 3000, service_charge=500),
        ]
        costs = [v.calculate_rental_cost(6) for v in vehicles]
        self.assertEqual(costs, [12000, 700 * 6 * 0.95, 3000 * 6 + 500])


class TestVehicleValidation(unittest.TestCase):
    def test_missing_registration_number_raises(self):
        with self.assertRaises(ValidationError):
            Car("V1", "", "Toyota", "Etios", 2000)

    def test_non_positive_daily_rate_raises(self):
        with self.assertRaises(ValidationError):
            Car("V1", "KA01AA0001", "Toyota", "Etios", 0)


class TestCustomerValidation(unittest.TestCase):
    def test_empty_name_raises(self):
        with self.assertRaises(ValidationError):
            Customer("C1", "", "a@b.com", "DL123")

    def test_invalid_email_raises(self):
        with self.assertRaises(ValidationError):
            Customer("C1", "Test", "not-an-email", "DL123")

    def test_valid_customer_created(self):
        c = Customer("C1", "Test User", "t@example.com", "DL123")
        self.assertEqual(c.customer_id, "C1")
        self.assertEqual(c.rental_history, [])


class TestPayment(unittest.TestCase):
    def test_card_number_is_masked_not_stored_plain(self):
        card = CardPayment("4111111111111234", "Test User")
        result = card.process_payment(1000)
        self.assertIn("1234", result.masked_reference)
        self.assertNotIn("4111111111111234", result.masked_reference)

    def test_upi_id_is_masked(self):
        upi = UpiPayment("rohit@upi")
        result = upi.process_payment(1000)
        self.assertTrue(result.masked_reference.endswith("@upi"))
        self.assertNotEqual(result.masked_reference, "rohit@upi")

    def test_zero_amount_payment_fails(self):
        card = CardPayment("4111111111111234", "Test User")
        with self.assertRaises(PaymentFailedError):
            card.process_payment(0)


class TestRentalWorkflow(unittest.TestCase):
    def setUp(self):
        self.service = RentalService()
        self.car = Car("V101", "KA01AB1234", "Toyota", "Etios", 2000)
        self.service.add_vehicle(self.car)
        self.customer_a = Customer("C001", "Ananya Sharma", "ananya@example.com", "DL1")
        self.customer_b = Customer("C002", "Rohit Verma", "rohit@example.com", "DL2")
        self.service.register_customer(self.customer_a)
        self.service.register_customer(self.customer_b)

    def test_successful_rental_marks_vehicle_unavailable(self):
        payment = CardPayment("4111111111111234", "Ananya Sharma")
        rental = self.service.rent_vehicle(self.customer_a, "V101", 3, payment)
        self.assertEqual(rental.status, "CONFIRMED")
        self.assertFalse(self.car.is_available)
        self.assertEqual(rental.base_amount, 6000)

    def test_cannot_rent_unavailable_vehicle(self):
        payment_a = CardPayment("4111111111111234", "Ananya Sharma")
        self.service.rent_vehicle(self.customer_a, "V101", 3, payment_a)

        payment_b = UpiPayment("rohit@upi")
        with self.assertRaises(VehicleUnavailableError):
            self.service.rent_vehicle(self.customer_b, "V101", 2, payment_b)

    def test_invalid_duration_rejected(self):
        payment = CardPayment("4111111111111234", "Ananya Sharma")
        with self.assertRaises(InvalidRentalDurationError):
            self.service.rent_vehicle(self.customer_a, "V101", 0, payment)

    def test_unknown_vehicle_id_rejected(self):
        payment = CardPayment("4111111111111234", "Ananya Sharma")
        with self.assertRaises(VehicleNotFoundError):
            self.service.rent_vehicle(self.customer_a, "V999", 2, payment)

    def test_payment_failure_prevents_rental_confirmation(self):
        """Vehicle must remain available if payment fails -- rental never created."""
        with self.assertRaises(PaymentFailedError):
            self.service.rent_vehicle(self.customer_a, "V101", 3, AlwaysFailsPayment())
        self.assertTrue(self.car.is_available)

    def test_on_time_return_has_no_late_fee(self):
        payment = CardPayment("4111111111111234", "Ananya Sharma")
        rental = self.service.rent_vehicle(self.customer_a, "V101", 3, payment)
        self.service.return_vehicle(rental.rental_id, rental.due_return_date)
        self.assertEqual(rental.late_fee, 0)
        self.assertTrue(self.car.is_available)

    def test_late_return_calculates_correct_late_fee(self):
        payment = CardPayment("4111111111111234", "Ananya Sharma")
        rental = self.service.rent_vehicle(self.customer_a, "V101", 3, payment)
        late_return = rental.due_return_date + timedelta(days=1)
        self.service.return_vehicle(rental.rental_id, late_return)
        # 1 late day x 20% of Rs.2000 daily rate = Rs.400
        self.assertEqual(rental.late_fee, 400)
        self.assertEqual(rental.total_amount, 6400)

    def test_return_updates_customer_history(self):
        payment = CardPayment("4111111111111234", "Ananya Sharma")
        rental = self.service.rent_vehicle(self.customer_a, "V101", 3, payment)
        self.service.return_vehicle(rental.rental_id, rental.due_return_date)
        self.assertEqual(len(self.customer_a.rental_history), 1)
        self.assertEqual(self.customer_a.rental_history[0].status, "RETURNED")

    def test_returning_unknown_rental_id_raises(self):
        with self.assertRaises(RentalNotFoundError):
            self.service.return_vehicle("R9999")


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.service = RentalService()
        self.service.add_vehicle(Car("V101", "KA01AB1234", "Toyota", "Etios", 2000))
        self.service.add_vehicle(Bike("V102", "KA01CD5678", "Yamaha", "FZ", 700))
        self.service.add_vehicle(Van("V103", "KA01EF9012", "Tata", "Winger", 3000))

    def test_search_by_id(self):
        result = self.service.search_vehicles(vehicle_id="V102")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].vehicle_type, "Bike")

    def test_search_by_type(self):
        result = self.service.search_vehicles(vehicle_type="Van")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].vehicle_id, "V103")

    def test_search_by_price_range(self):
        result = self.service.search_vehicles(min_price=1000, max_price=2500)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].vehicle_id, "V101")

    def test_search_with_no_filters_returns_all(self):
        result = self.service.search_vehicles()
        self.assertEqual(len(result), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)

# Test Cases — Vehicle Rental Management System

All 26 automated tests live in `tests/test_rental_system.py` and pass
(see `docs/test_run_output.txt` for the raw run). The table below restates
each one as a manual test case with expected vs. actual result, as the
assignment asks for.

Run them yourself with:
```
python -m unittest tests.test_rental_system -v
```

## Success paths

| # | Test case | Steps | Expected result | Actual result |
|---|-----------|-------|------------------|----------------|
| 1 | Car cost calculation | Create Car, daily rate 2000, rent 3 days | 6000 | 6000 — Pass |
| 2 | Bike cost, ≤5 days | Create Bike, daily rate 700, rent 5 days | 3500 (no discount) | 3500 — Pass |
| 3 | Bike cost, >5 days | Create Bike, daily rate 700, rent 6 days | 3990 (5% discount) | 3990.0 — Pass |
| 4 | Van cost with service charge | Daily rate 3000, service charge 500, 2 days | 6500 | 6500 — Pass |
| 5 | Polymorphic dispatch | Call `calculate_rental_cost(6)` on Car/Bike/Van via a common `Vehicle` reference | Each returns its own type-specific value with no `if/elif` on type | [12000, 3990.0, 18500] — Pass |
| 6 | Valid customer registration | Register customer with all fields filled | Customer created, empty rental history | Created — Pass |
| 7 | Card payment masking | Pay with card `4111111111111234` | Stored reference shows only last 4 digits | `**** **** **** 1234` — Pass |
| 8 | UPI payment masking | Pay with UPI id `rohit@upi` | Handle partially masked, provider kept | `r****@upi` — Pass |
| 9 | Successful rental | Customer A rents Car V101 for 3 days with valid card | Rental status `CONFIRMED`, vehicle becomes unavailable | Confirmed, unavailable — Pass |
| 10 | On-time return | Return exactly on due date | Late fee = 0, vehicle available again | 0, available — Pass |
| 11 | Late return | Return 1 day after due date, daily rate 2000 | Late fee = 1 × 20% × 2000 = 400; final = 6400 | 400 / 6400 — Pass |
| 12 | Customer history updated | Return a rental | Rental appears in customer's history with status `RETURNED` | Present, `RETURNED` — Pass |
| 13 | Search by ID | Search `vehicle_id="V102"` | Returns exactly the Bike V102 | 1 result, Bike — Pass |
| 14 | Search by type | Search `vehicle_type="Van"` | Returns exactly the Van | 1 result, V103 — Pass |
| 15 | Search by price range | Search 1000–2500 | Returns only the Car (2000/day) | 1 result, V101 — Pass |
| 16 | Search with no filters | Call with no arguments | Returns all vehicles | 3 results — Pass |

## Failure / validation paths

| # | Test case | Steps | Expected result | Actual result |
|---|-----------|-------|------------------|----------------|
| 17 | Empty registration number | Create a Car with `registration_number=""` | `ValidationError` raised | Raised — Pass |
| 18 | Non-positive daily rate | Create a Car with `daily_rate=0` | `ValidationError` raised | Raised — Pass |
| 19 | Empty customer name | Register a customer with `name=""` | `ValidationError` raised | Raised — Pass |
| 20 | Invalid email | Register a customer with `email="not-an-email"` | `ValidationError` raised | Raised — Pass |
| 21 | Zero-amount payment | Call `process_payment(0)` on a CardPayment | `PaymentFailedError` raised | Raised — Pass |
| 22 | Rent an already-rented vehicle | Customer A rents V101, then Customer B tries to rent V101 | `VehicleUnavailableError` raised for Customer B | Raised — Pass |
| 23 | Invalid rental duration | Attempt to rent for 0 days | `InvalidRentalDurationError` raised | Raised — Pass |
| 24 | Unknown vehicle ID | Attempt to rent `"V999"` | `VehicleNotFoundError` raised | Raised — Pass |
| 25 | Payment failure blocks rental | Use a payment processor that always raises `PaymentFailedError` | Rental is never created; vehicle stays available | Raised, vehicle still available — Pass |
| 26 | Return unknown rental | Call `return_vehicle("R9999")` | `RentalNotFoundError` raised | Raised — Pass |

**Summary: 26 / 26 automated tests passing.**

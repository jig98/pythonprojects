# Vehicle Rental Management System

A console-based vehicle rental system built for the Fresher Training OOP
Case Study. It models cars, bikes, and vans, customers, rentals, returns,
payments, and invoicing using proper object-oriented design.

## 1. Project description

A vehicle rental company rents cars, bikes, and vans to customers. This
application lets a customer search available vehicles, rent one, return
it, pay for it, and receive an invoice — while the system enforces the
company's business rules (no double-booking, no rental without payment,
late fees, etc.).

## 2. Project structure

```
vehicle_rental_system/
├── main.py                          # Runs the mandatory demo scenario
├── models/
│   ├── vehicle.py                   # Vehicle (abstract), Car, Bike, Van
│   ├── customer.py                  # Customer
│   ├── payment.py                   # PaymentProcessor, CardPayment, UpiPayment
│   ├── rental.py                    # Rental
│   └── invoice.py                   # Invoice
├── services/
│   └── rental_service.py            # RentalService — the workflow orchestrator
├── exceptions/
│   └── custom_exceptions.py         # All custom exception classes
├── tests/
│   └── test_rental_system.py        # 26 automated unit tests
└── docs/
    ├── class_diagram.png            # Class diagram
    ├── test_cases.md                # Test cases with expected/actual results
    ├── test_run_output.txt          # Captured test run
    └── mandatory_scenario_console_output.txt   # Captured demo scenario output
```

## 3. How to run it

### Windows (PowerShell)

1. Make sure Python 3.10+ is installed:
   ```powershell
   python --version
   ```
2. Open PowerShell in the project folder (adjust the path to wherever you
   saved it, e.g. under OneDrive):
   ```powershell
   cd "C:\Users\<you>\OneDrive\Documents\vehicle_rental_system"
   ```
3. Run the mandatory demonstration scenario:
   ```powershell
   python main.py
   ```
4. Run the automated test suite:
   ```powershell
   python -m unittest tests.test_rental_system -v
   ```
   If PowerShell blocks script execution for anything else you run
   alongside this (e.g. a venv activation script), that's a separate
   execution-policy setting — running `python main.py` directly does not
   need it.

### macOS / Linux

```bash
cd vehicle_rental_system
python3 main.py
python3 -m unittest tests.test_rental_system -v
```

No external dependencies are required — everything uses the Python
standard library only.

## 4. Class responsibilities

| Class | Responsibility |
|---|---|
| `Vehicle` (abstract) | Common vehicle data (id, registration, brand, model, daily rate, availability) and the `calculate_rental_cost()` contract every vehicle type must implement. |
| `Car`, `Bike`, `Van` | Each implements its own pricing rule: Car is linear, Bike discounts long rentals, Van adds a service charge. |
| `Customer` | Identity details, validation, and the list of past `Rental`s. |
| `PaymentProcessor` (interface) | Defines `process_payment(amount)`. `CardPayment` and `UpiPayment` implement it and store only masked references, never raw card/UPI numbers. |
| `Rental` | Composes a `Customer`, a `Vehicle`, and a `PaymentResult`; owns the rental-days validation, due-date, and late-fee math. |
| `Invoice` | Formats a completed `Rental` into a printable breakdown. |
| `RentalService` | Orchestrates the whole workflow — search, rent, return — and enforces business rules. Depends only on the `PaymentProcessor` interface, never on a concrete payment class. |
| Custom exceptions | `ValidationError`, `InvalidRentalDurationError`, `VehicleUnavailableError`, `VehicleNotFoundError`, `PaymentFailedError`, `RentalNotFoundError` — each named after the specific business rule it protects. |

## 5. OOP concept mapping

| Concept | Where it shows up |
|---|---|
| **Classes & objects** | `Vehicle`, `Customer`, `Rental`, `Invoice`, `PaymentProcessor` and their concrete instances. |
| **Encapsulation** | Every class stores its fields as private attributes (`__field`) and exposes them only through read-only `@property` getters; state changes go through methods like `mark_as_rented()` that can enforce rules. |
| **Abstraction** | `Vehicle` and `PaymentProcessor` are `ABC`s — they define *what* must be done, not *how*. Callers work against these abstractions. |
| **Inheritance** | `Car`, `Bike`, `Van` inherit from `Vehicle`; `CardPayment`, `UpiPayment` inherit from `PaymentProcessor`. |
| **Polymorphism** | `RentalService` and `Rental` call `vehicle.calculate_rental_cost(days)` without knowing or checking the concrete subclass — each subclass's own override runs. See §6 below. |
| **Interface** | `PaymentProcessor` is an abstract class used purely as a contract (single abstract method, no shared state) — Python's equivalent of a Java/C# interface. |
| **Method overriding** | `Car`, `Bike`, `Van` each override `calculate_rental_cost()`. |
| **Method overloading** | Python has no native overload syntax (a second `def` with the same name replaces the first), so `RentalService.search_vehicles()` offers a single entry point with optional parameters (`vehicle_id`, `vehicle_type`, `min_price`/`max_price`) that dispatches to three distinct private search behaviours — the intent Java/C# overloading expresses, done the idiomatic Python way. |
| **Composition** | A `Rental` *has-a* `Customer`, a `Vehicle`, and a `PaymentResult` — modelled as direct object references stored at construction time. |
| **Association** | A `Customer` accumulates many `Rental`s over time (`rental_history`), independent of any one rental's lifecycle. |
| **Exception handling** | Invalid days → `InvalidRentalDurationError`; unavailable vehicle → `VehicleUnavailableError`; payment failure → `PaymentFailedError`; each caught and reported with a meaningful message instead of crashing. |

## 6. Where polymorphism is used, and why it helps

`RentalService.rent_vehicle()` and `Rental.__init__()` both call:

```python
base_amount = vehicle.calculate_rental_cost(days)
```

`vehicle` is typed as `Vehicle`, but at runtime it might be a `Car`, `Bike`,
or `Van`. Because each subclass overrides `calculate_rental_cost()`, the
correct pricing rule runs automatically — the calling code never asks
`if vehicle.type == "Car": ... elif vehicle.type == "Bike": ...`.

This is exactly what the assignment's design expectation asks for
("avoid long if/else chains based on vehicle type"), and it pays off
directly for extensibility: adding a fourth vehicle type (say, `Truck`)
means writing one new class with its own `calculate_rental_cost()` —
`RentalService` does not change at all. That satisfies the open/closed
principle: the system is open to new vehicle types but closed to
modification of existing, already-tested code.

## 7. Business rules enforced

- Rental days must be a positive whole number (`InvalidRentalDurationError` otherwise).
- A customer cannot rent an unavailable vehicle (`VehicleUnavailableError`).
- The same vehicle cannot be rented by two customers at once — enforced by
  the `available` flag flipping to `False` the instant a rental is confirmed.
- Every vehicle requires a non-empty registration number (`ValidationError`).
- Payment is always attempted and must succeed *before* the vehicle is
  marked unavailable or the `Rental` object is created — see the ordering
  in `RentalService.rent_vehicle()`.
- Card numbers and UPI IDs are masked immediately on input; the raw values
  are never stored as attributes or printed anywhere.
- Returning a vehicle always sets it back to available.
- Every failure path raises a specific, named exception with a readable
  message rather than a generic crash.

## 8. Mandatory demonstration scenario

`main.py` runs all 12 steps from the assignment in order (add vehicles,
register customers, list availability, rent the car to Customer A, attempt
— and correctly fail — to rent it to Customer B, process payment, return
the car a day late, compute the late fee and final invoice, confirm the
vehicle is available again, and show Customer A's history).

The captured output is saved at
`docs/mandatory_scenario_console_output.txt` and matches the assignment's
sample numbers exactly: base amount Rs. 6,000, late fee Rs. 400, final
amount Rs. 6,400.

## 9. Testing

26 automated unit tests in `tests/test_rental_system.py` cover both
success paths (correct pricing per vehicle type, successful rentals,
on-time and late returns, search variants) and failure paths (empty
fields, invalid duration, double-booking, unknown IDs, payment failure).
All 26 pass — see `docs/test_run_output.txt` and `docs/test_cases.md` for
the full breakdown with expected vs. actual results.

## 10. Discussion questions (short answers)

1. **Why should `Vehicle` be abstract?** No generic "vehicle" is ever
   rented in real life — every instance is a Car, Bike, or Van, each with
   its own pricing rule. Making `Vehicle` abstract stops anyone from
   creating an object that has no defined `calculate_rental_cost()`.
2. **How does polymorphism remove vehicle-type conditionals?** Calling
   code invokes `vehicle.calculate_rental_cost(days)` on the shared base
   type; the object itself resolves which override to run, so no
   type-checking branch is needed anywhere else in the system.
3. **Why should vehicle and customer fields remain private?** So state
   can only change through methods that validate it (`mark_as_rented`,
   `add_rental`, etc.), preventing another part of the program from, say,
   setting a negative daily rate or silently deleting rental history.
4. **Relationship between `Rental`, `Customer`, and `Vehicle`?** `Rental`
   is composed of one `Customer` and one `Vehicle` (composition); a
   `Customer`, in turn, is associated with many `Rental`s over its
   lifetime.
5. **Adding a new vehicle type without changing existing classes?**
   Create a new subclass of `Vehicle` implementing
   `calculate_rental_cost()`. `RentalService`, `Rental`, and `Invoice`
   never need to change because they only depend on the `Vehicle`
   abstraction.
6. **What should happen when payment processing fails?** `PaymentFailedError`
   is raised, no `Rental` object is created, and the vehicle's
   availability is untouched — the failed attempt has zero side effects.
7. **Which parts demonstrate composition?** `Rental` holding direct
   references to a `Customer`, `Vehicle`, and `PaymentResult`; `Invoice`
   holding a reference to the `Rental` it summarises.
8. **If one booking could contain multiple vehicles?** `Rental` would
   hold a list of `Vehicle`s (and per-vehicle cost lines) instead of a
   single one, `calculate_final_amount()` would sum across that list, and
   `RentalService.rent_vehicle()` would need to check *and* reserve every
   vehicle in the booking atomically so a partial failure doesn't leave
   some vehicles marked unavailable while others remain bookable.

# Vehicle Rental Management System

An interactive, console-based vehicle rental system built for the Fresher
Training OOP Case Study. Everything happens through a live terminal menu:
adding vehicles, registering customers, renting, returning, paying, and
invoicing — all driven by real user input, not a scripted demo.

## 1. Project description

A vehicle rental company rents cars, bikes, and vans to customers. Run
`main.py` and you get a menu-driven terminal application: search
available vehicles, register yourself as a customer, rent a vehicle, pay
for it, return it later, and view your invoice and rental history — while
the system enforces the company's business rules behind the scenes (no
double-booking, no rental without payment, correct late fees, etc.).

## 2. Project structure

```
vehicle_rental_system/
├── main.py                          # Entry point -- run this
├── cli/
│   ├── app.py                       # RentalApp -- the interactive menu loop
│   ├── console_io.py                # Input-validation helpers (prompt_str, prompt_int, ...)
│   └── activity_log.py              # ActivityLogger -- saves every operation to JSON
├── models/
│   ├── vehicle.py                   # Vehicle (abstract), Car, Bike, Van
│   ├── customer.py                  # Customer
│   ├── payment.py                   # PaymentProcessor, CardPayment, UpiPayment
│   ├── rental.py                    # Rental
│   └── invoice.py                   # Invoice
├── services/
│   └── rental_service.py            # RentalService -- the workflow orchestrator
├── exceptions/
│   └── custom_exceptions.py         # All custom exception classes
├── data/
│   └── activity_log.json            # Created automatically -- every operation's record
└── docs/
    ├── class_diagram.png            # Class diagram
    ├── test_cases.md                # Manual test cases with expected/actual results
    ├── sample_terminal_session.txt  # A full recorded run of the CLI
    └── sample_activity_log.json     # Example of what gets logged in one session
```

## 3. How to run it

### Windows (PowerShell)

1. Confirm Python 3.10+ is installed:
   ```powershell
   python --version
   ```
2. `cd` into the project folder (adjust to wherever you saved it):
   ```powershell
   cd "C:\Users\<you>\OneDrive\Documents\vehicle_rental_system"
   ```
3. Start the application:
   ```powershell
   python main.py
   ```
4. Follow the on-screen menu — type a number and press Enter at each
   prompt.

### macOS / Linux

```bash
cd vehicle_rental_system
python3 main.py
```

No external dependencies are required — everything uses the Python
standard library only.

## 4. What happens when you run it

The program preloads a small starting inventory (1 Car, 1 Bike, 1 Van —
matching the assignment's sample vehicles) so the menu isn't empty, then
shows this menu on a loop until you choose **Exit**:

```
==================================================
        VEHICLE RENTAL MANAGEMENT SYSTEM
==================================================
 1. View available vehicles
 2. Search vehicles
 3. Register a new customer
 4. Rent a vehicle
 5. Return a vehicle
 6. View a rental invoice
 7. View a customer's rental history
 8. Add a new vehicle (admin)
 9. Exit
==================================================
```

Every option is fully interactive:
- **Rent a vehicle** asks for your customer ID (or lets you register on
  the spot), shows available vehicles, checks the one you picked is
  actually free *before* asking for payment details, then asks you to
  choose Card or UPI and collects the details for that method.
- **Return a vehicle** asks for the rental ID and how many days late (0
  if on time), then prints the full invoice with base amount, late fee,
  and final amount.
- Every input is validated in a loop (empty fields, non-numbers, invalid
  menu choices) so a typo never crashes the program — you just get a
  clear message and another chance to type it correctly.

A full recorded session is saved at `docs/sample_terminal_session.txt` if
you want to see the exact output without running it yourself first.

## 5. Every action is saved to a JSON log

Alongside everything printed to the screen, `RentalApp` writes a permanent
record of every operation -- successful, blocked, or failed -- to
`data/activity_log.json`. This file is created automatically the first
time you run the program, and **new entries are appended to it on every
run** (it's never wiped on startup), so it becomes a running history of
everything the system has ever done.

Each entry looks like this:

```json
{
  "timestamp": "2026-09-04T03:52:29",
  "action": "rent_vehicle",
  "status": "success",
  "details": {
    "rental_id": "R0001",
    "customer_id": "C001",
    "customer_name": "Ananya Sharma",
    "vehicle_id": "V101",
    "vehicle_type": "Car",
    "rental_days": 3,
    "base_amount": 6000.0,
    "due_return_date": "2026-09-07",
    "payment_method": "Card",
    "payment_reference": "**** **** **** 1234",
    "transaction_id": "CARD-TXN-0001"
  }
}
```

`status` is one of:
- **`success`** -- the operation completed normally.
- **`blocked`** -- the CLI caught a problem itself before it became an
  exception (e.g. trying to rent an already-rented vehicle, or return an
  already-returned one) -- the `details.reason` field says why.
- **`error`** -- a `RentalSystemError` was raised and caught in the main
  menu loop -- `details.error_type` and `details.message` capture it.

Every menu option logs something relevant to what it does:

| Option | What gets logged |
|---|---|
| View available vehicles | The full list of currently available vehicles |
| Search vehicles | The search criteria used and every result found |
| Register a new customer | The new customer's details (or a `blocked` entry if the ID was already taken) |
| Rent a vehicle | Rental ID, customer, vehicle, days, amount, due date, and payment reference -- or a `blocked` entry with the reason if the vehicle didn't exist or wasn't available |
| Return a vehicle | Return date, late days, late fee, and final total |
| View a rental invoice | The rental's cost breakdown |
| View a customer's rental history | Every rental in that customer's history |
| Add a new vehicle | The new vehicle's full details |

See `docs/sample_activity_log.json` for a complete example from a real
session (register two customers, rent a car, a blocked double-booking
attempt, a late return, an invoice lookup, a history lookup, adding a
vehicle, and a search) — that single file is a machine-readable
transcript of everything demonstrated in `docs/sample_terminal_session.txt`.

## 6. Class responsibilities

| Class | Responsibility |
|---|---|
| `RentalApp` (`cli/app.py`) | The terminal front-end: prints the menu, reads input, calls into `RentalService`, logs every outcome via `ActivityLogger`, and turns any `RentalSystemError` into a friendly on-screen message. Contains no business logic itself. |
| `ActivityLogger` (`cli/activity_log.py`) | Appends a structured JSON entry — action, status, and relevant details — to `data/activity_log.json` after every operation. |
| `console_io` helpers | Reusable, self-looping input functions (`prompt_str`, `prompt_int`, `prompt_float`, `prompt_choice`, `prompt_yes_no`) so every menu handler validates input the same way. |
| `Vehicle` (abstract) | Common vehicle data (id, registration, brand, model, daily rate, availability) and the `calculate_rental_cost()` contract every vehicle type must implement. |
| `Car`, `Bike`, `Van` | Each implements its own pricing rule: Car is linear, Bike discounts long rentals, Van adds a service charge. |
| `Customer` | Identity details, validation, and the list of past `Rental`s. |
| `PaymentProcessor` (interface) | Defines `process_payment(amount)`. `CardPayment` and `UpiPayment` implement it and store only masked references, never raw card/UPI numbers. |
| `Rental` | Composes a `Customer`, a `Vehicle`, and a `PaymentResult`; owns the rental-days validation, due-date, and late-fee math. |
| `Invoice` | Formats a completed `Rental` into a printable breakdown. |
| `RentalService` | Orchestrates the whole workflow — search, rent, return, invoice lookup — and enforces business rules. Depends only on the `PaymentProcessor` interface, never on a concrete payment class. The CLI is the only thing that talks to it directly. |
| Custom exceptions | `ValidationError`, `InvalidRentalDurationError`, `VehicleUnavailableError`, `VehicleNotFoundError`, `PaymentFailedError`, `RentalNotFoundError` — each named after the specific business rule it protects, all caught centrally in `RentalApp.run()`. |

## 7. OOP concept mapping

| Concept | Where it shows up |
|---|---|
| **Classes & objects** | `Vehicle`, `Customer`, `Rental`, `Invoice`, `PaymentProcessor`, `RentalApp` and their instances. |
| **Encapsulation** | Every model class stores fields as private attributes (`__field`) and exposes them only through read-only `@property` getters; state changes go through methods like `mark_as_rented()` that can enforce rules. |
| **Abstraction** | `Vehicle` and `PaymentProcessor` are `ABC`s — they define *what* must be done, not *how*. `RentalApp` only ever talks to `RentalService`, never touching private state directly. |
| **Inheritance** | `Car`, `Bike`, `Van` inherit from `Vehicle`; `CardPayment`, `UpiPayment` inherit from `PaymentProcessor`. |
| **Polymorphism** | `RentalService` and `Rental` call `vehicle.calculate_rental_cost(days)` without knowing or checking the concrete subclass — each subclass's own override runs. See §8 below. |
| **Interface** | `PaymentProcessor` is an abstract class used purely as a contract (single abstract method, no shared state) — Python's equivalent of a Java/C# interface. The CLI's payment menu picks the concrete class; everything downstream depends only on the interface. |
| **Method overriding** | `Car`, `Bike`, `Van` each override `calculate_rental_cost()`. |
| **Method overloading** | Python has no native overload syntax, so `RentalService.search_vehicles()` offers one entry point with optional parameters (`vehicle_id`, `vehicle_type`, `min_price`/`max_price`) dispatching to three distinct private search behaviours — the CLI's search menu (option 2) exercises all three. |
| **Composition** | A `Rental` *has-a* `Customer`, a `Vehicle`, and a `PaymentResult` — direct object references stored at construction time. |
| **Association** | A `Customer` accumulates many `Rental`s over time (`rental_history`), independent of any one rental's lifecycle. |
| **Exception handling** | Invalid days, unavailable vehicle, payment failure, unknown IDs, duplicate registrations — every one raises a specific exception, and `RentalApp.run()` catches the common `RentalSystemError` base class in one place so no menu handler needs its own try/except boilerplate. |

## 8. Where polymorphism is used, and why it helps

`RentalService.rent_vehicle()` and `Rental.__init__()` both call:

```python
base_amount = vehicle.calculate_rental_cost(days)
```

`vehicle` is typed as `Vehicle`, but at runtime it might be a `Car`,
`Bike`, or `Van` — whichever one you picked from the terminal menu.
Because each subclass overrides `calculate_rental_cost()`, the correct
pricing rule runs automatically; the calling code never asks
`if vehicle.type == "Car": ... elif ...`.

This pays off directly for extensibility: adding a fourth vehicle type
(say, `Truck`) via the terminal's "Add a new vehicle" option would only
need one new class with its own `calculate_rental_cost()` — `RentalApp`
and `RentalService` would not change at all.

## 9. Business rules enforced

- Rental days must be a positive whole number — the terminal loops until
  you type a valid one (`InvalidRentalDurationError` if bypassed
  programmatically).
- A customer cannot rent an unavailable vehicle — checked and reported
  *before* the payment step even starts.
- The same vehicle cannot be rented by two customers at once — the
  `available` flag flips to `False` the instant a rental is confirmed.
- Every vehicle requires a non-empty registration number.
- Payment is always attempted and must succeed *before* the vehicle is
  marked unavailable or the `Rental` object is created.
- Card numbers and UPI IDs are masked immediately on input; the raw
  values are never stored as attributes or printed anywhere in the
  terminal.
- Returning a vehicle always sets it back to available.
- Every failure path raises a specific, named exception with a readable
  message, caught centrally and shown as `[Error] ...` — the menu never
  crashes.

## 10. Testing

Because this is now a live interactive program, testing is done by
running the menu yourself rather than a separate automated script. 20
manual test cases (11 success paths, 9 failure/validation paths) are
documented with expected vs. actual results in `docs/test_cases.md`, and
`docs/sample_terminal_session.txt` is a full recorded run covering
registration, renting, a blocked double-booking, a late return, invoice
lookup, rental history, and adding a new vehicle — all matching the
assignment's sample numbers exactly (base Rs. 6,000, late fee Rs. 400,
final Rs. 6,400).

## 11. Discussion questions (short answers)

1. **Why should `Vehicle` be abstract?** No generic "vehicle" is ever
   rented in real life — every instance is a Car, Bike, or Van, each with
   its own pricing rule. Making `Vehicle` abstract stops anyone from
   creating an object with no defined `calculate_rental_cost()`.
2. **How does polymorphism remove vehicle-type conditionals?** Calling
   code invokes `vehicle.calculate_rental_cost(days)` on the shared base
   type; the object itself resolves which override to run, so no
   type-checking branch is needed anywhere else in the system — including
   in `RentalApp`, which never asks what kind of vehicle you rented.
3. **Why should vehicle and customer fields remain private?** So state
   can only change through methods that validate it (`mark_as_rented`,
   `add_rental`, etc.), preventing any part of the program — including
   the terminal layer — from setting a negative daily rate or silently
   corrupting rental history.
4. **Relationship between `Rental`, `Customer`, and `Vehicle`?** `Rental`
   is composed of one `Customer` and one `Vehicle` (composition); a
   `Customer`, in turn, is associated with many `Rental`s over its
   lifetime.
5. **Adding a new vehicle type without changing existing classes?**
   Create a new subclass of `Vehicle` implementing
   `calculate_rental_cost()`. `RentalService`, `Rental`, `Invoice`, and
   `RentalApp` never need to change because they only depend on the
   `Vehicle` abstraction.
6. **What should happen when payment processing fails?**
   `PaymentFailedError` is raised, no `Rental` object is created, the
   vehicle's availability is untouched, and the terminal shows
   `[Error] ...` and returns to the menu — the failed attempt has zero
   side effects.
7. **Which parts demonstrate composition?** `Rental` holding direct
   references to a `Customer`, `Vehicle`, and `PaymentResult`; `Invoice`
   holding a reference to the `Rental` it summarises.
8. **If one booking could contain multiple vehicles?** `Rental` would
   hold a list of `Vehicle`s (and per-vehicle cost lines) instead of a
   single one, `calculate_final_amount()` would sum across that list, the
   terminal's "Rent a vehicle" flow would loop to collect multiple
   vehicle IDs, and `RentalService.rent_vehicle()` would need to check
   *and* reserve every vehicle in the booking atomically so a partial
   failure doesn't leave some vehicles marked unavailable while others
   remain bookable.

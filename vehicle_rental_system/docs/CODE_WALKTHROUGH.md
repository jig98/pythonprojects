# Code Walkthrough — Vehicle Rental Management System

This is a line-by-line explanation of every file, in the order you'd
naturally explain the project: exceptions first (everything else depends
on them), then the model classes (`Vehicle`, `Customer`, `Payment`,
`Rental`, `Invoice`), then the service layer (`RentalService`), then the
terminal/CLI layer (`console_io.py`, `app.py`, `main.py`).

**How to use this tonight:** read each section once, then try explaining
it out loud without looking — that's the real test of whether you can
present it tomorrow.

---

## 0. The big picture (say this first)

The project has four layers, each only knowing about the layer directly
below it:

```
main.py  -->  cli/ (terminal menu)  -->  services/ (business rules)  -->  models/ (data + core logic)
                                                                            exceptions/ (used everywhere)
```

- **`exceptions/`** — custom error types used across the whole project.
- **`models/`** — the "nouns" of the system: `Vehicle`, `Customer`,
  `PaymentProcessor`, `Rental`, `Invoice`. They hold data and know how to
  validate/calculate things about *themselves*, but don't know about the
  menu or the workflow.
- **`services/rental_service.py`** — the "verbs": search, rent, return.
  This is where business rules are enforced (no double booking, payment
  before confirmation, etc.).
- **`cli/`** — the terminal menu. It only talks to `RentalService`; it
  never touches a model's private data directly.

If asked "why split it like this?" — the answer is **separation of
concerns**: you could swap the terminal menu for a web page tomorrow and
none of `models/` or `services/` would need to change.

---

## 1. `exceptions/custom_exceptions.py`

```python
class RentalSystemError(Exception):
    """Base class for every exception raised by this application."""
    pass
```
**Line by line:**
- `class RentalSystemError(Exception):` — defines a new exception type by
  inheriting from Python's built-in `Exception` class. This is the
  **parent** of every custom error in the project.
- `pass` — the class body has nothing extra to add; it exists purely to
  give this family of errors a name. The docstring above `pass` explains
  its purpose.

```python
class ValidationError(RentalSystemError):
    """Raised when a required field is empty or otherwise invalid."""
    pass
```
- Inherits from `RentalSystemError`, not from `Exception` directly. That
  means: `except RentalSystemError` will catch a `ValidationError` too,
  because of inheritance — a `ValidationError` *is a* `RentalSystemError`.

The same pattern repeats for the other five:
`InvalidRentalDurationError`, `VehicleUnavailableError`,
`VehicleNotFoundError`, `PaymentFailedError`, `RentalNotFoundError`.
Each one is named after **exactly one business rule** it protects — when
one of these is raised anywhere in the app, you instantly know which rule
was broken just from the exception's name.

**Why this design, if asked:** Instead of catching generic `Exception` (too
broad — would also hide real bugs) or writing six separate `except`
blocks everywhere (repetitive), the code can do `except RentalSystemError`
**once** in the CLI (see `cli/app.py` §9 below) and it correctly catches
all six specific error types, because they all share this one parent.

---

## 2. `models/vehicle.py` — the most important file to understand well

This is where **abstraction, inheritance, encapsulation, and
polymorphism** all live, so expect the most questions here.

```python
from abc import ABC, abstractmethod
```
- `ABC` = "Abstract Base Class." Importing it from Python's built-in
  `abc` module lets us build a class that **cannot be instantiated
  directly** — you can never write `Vehicle(...)` and get an object back.
  Only its subclasses (`Car`, `Bike`, `Van`) can be instantiated.
- `abstractmethod` is a decorator (a label you put above a method) that
  marks a method as "every subclass MUST implement this, or Python will
  refuse to let you create that subclass."

```python
class Vehicle(ABC):
```
- Declares `Vehicle` as a class that inherits from `ABC`. This one word,
  `ABC`, is what turns on the "can't be instantiated directly" behaviour.
  **This is abstraction**: `Vehicle` describes *what* every vehicle must
  be able to do, without saying *how*.

```python
    def __init__(self, vehicle_id: str, registration_number: str,
                 brand: str, model: str, daily_rate: float):
```
- `__init__` is the **constructor** — the method Python calls
  automatically when you create a new object, e.g. `Car("V101", ...)`.
- `self` refers to the specific object being built (every instance
  method's first parameter is `self` by convention).
- The rest are the five pieces of data every vehicle needs, each with a
  **type hint** (`: str`, `: float`) — these don't enforce anything at
  runtime, they're documentation for humans and IDEs.

```python
        if not vehicle_id or not str(vehicle_id).strip():
            raise ValidationError("Vehicle ID cannot be empty.")
```
- `not vehicle_id` catches `None` or an empty string `""`.
- `.strip()` removes leading/trailing spaces, so a string of just spaces
  (`"   "`) is also caught — `"   ".strip()` becomes `""`, which is falsy.
- If either check fails, `raise` immediately stops execution and throws a
  `ValidationError` with a message explaining exactly what went wrong.
- The next four `if` blocks (lines 31–38 in the file) repeat this same
  pattern for `registration_number`, `brand`, `model`, and `daily_rate`
  (the last one checks `daily_rate <= 0` instead of emptiness, since it's
  a number, not a string).

```python
        self.__vehicle_id = vehicle_id
        self.__registration_number = registration_number
        self.__brand = brand
        self.__model = model
        self.__daily_rate = float(daily_rate)
        self.__available = True
```
- **This is encapsulation.** The double leading underscore (`__field`)
  triggers Python's **name mangling**: internally, `self.__vehicle_id`
  actually gets stored as `self._Vehicle__vehicle_id`. This makes it
  awkward (effectively private) for code outside the class to reach in
  and change `vehicle.__vehicle_id` directly — they're forced to go
  through the methods/properties we define below instead.
- `float(daily_rate)` converts whatever number type was passed in
  (int or float) into a consistent `float`, so later math is predictable.
- `self.__available = True` — every new vehicle starts out available for
  rent.

```python
    @property
    def vehicle_id(self) -> str:
        return self.__vehicle_id
```
- `@property` turns a method into something that's *read* like a plain
  attribute: elsewhere in the code we write `car.vehicle_id`, not
  `car.vehicle_id()`. There's no matching setter defined, so
  `car.vehicle_id = "X"` would raise an `AttributeError` if anyone tried
  it — **this makes the field effectively read-only from outside the
  class**, which is exactly the point of encapsulation: outside code can
  *look* but can't *touch*.
- The same `@property` pattern repeats for `registration_number`,
  `brand`, `model`, `daily_rate`, and `is_available`.

```python
    @property
    def vehicle_type(self) -> str:
        """Returns the concrete subclass name, e.g. 'Car', 'Bike', 'Van'."""
        return type(self).__name__
```
- `type(self)` gets the *actual* class of the object at runtime — if
  `self` is a `Car` object, `type(self)` is the `Car` class itself.
- `.__name__` gets that class's name as a string, e.g. `"Car"`.
- So even though this method is written once on the parent `Vehicle`
  class, calling it on a `Bike` object returns `"Bike"`, on a `Van`
  returns `"Van"`, automatically — no `if/elif` needed.

```python
    def mark_as_rented(self) -> None:
        if not self.__available:
            raise ValidationError(f"Vehicle {self.__vehicle_id} is already rented.")
        self.__available = False

    def mark_as_available(self) -> None:
        self.__available = True
```
- These two methods are the **only** way `__available` can change from
  outside the class. `mark_as_rented()` refuses to run if the vehicle is
  already rented — this is what stops the "same vehicle rented twice"
  bug. Because `__available` is private, nobody can just do
  `car.__available = False` and skip this check (well — they'd hit the
  name-mangled attribute, not the real one, so it silently wouldn't work
  as intended, which is exactly the protection we want).

```python
    @abstractmethod
    def calculate_rental_cost(self, days: int) -> float:
        """Return the base rental cost for the given number of days."""
        raise NotImplementedError
```
- **This is the abstract method** — the contract. Because of
  `@abstractmethod`, Python will raise a `TypeError` at the moment you
  try to create any subclass that doesn't override this method. The
  `raise NotImplementedError` line inside never actually runs in
  practice (subclasses always override it), it's just a safety net.

```python
    def display_details(self) -> str:
        status = "Available" if self.__available else "Rented"
        return (f"{self.__vehicle_id} | {self.vehicle_type} | {self.__brand} "
                f"{self.__model} | Rs. {self.__daily_rate:,.0f} per day | {status}")
```
- `"Available" if self.__available else "Rented"` is a **conditional
  expression** (a one-line if/else that produces a value).
- `f"..."` is an f-string — anything inside `{}` gets evaluated and
  inserted into the string.
- `{self.__daily_rate:,.0f}` is a **format spec**: `,` adds thousand
  separators (2000 → "2,000"), `.0f` shows it as a fixed-point number
  with 0 decimal places.
- Notice this method calls `self.vehicle_type` (the property from
  above) — it doesn't need to know if `self` is a Car, Bike, or Van.

```python
    def __str__(self) -> str:
        return self.display_details()
```
- `__str__` is a **dunder (double-underscore) method** — Python calls it
  automatically whenever you do `print(some_vehicle)` or `str(some_vehicle)`.
  Here it just reuses `display_details()` so we don't repeat the format.

### Now the three subclasses — this is the polymorphism payoff

```python
class Car(Vehicle):
    """Car cost = daily rate x rental days. No special adjustment."""

    def calculate_rental_cost(self, days: int) -> float:
        return self.daily_rate * days
```
- `class Car(Vehicle):` — **inheritance**. `Car` automatically gets
  `__init__`, all the `@property` getters, `mark_as_rented`,
  `mark_as_available`, `display_details`, and `__str__` from `Vehicle`
  for free, without rewriting any of them.
- It only writes the one method it needs to specialize:
  `calculate_rental_cost`. This **overrides** the abstract version from
  the parent — this satisfies the abstract contract, so `Car` can now be
  instantiated.
- The formula itself is simple: `self.daily_rate` (inherited property)
  times `days` (the parameter passed in).

```python
class Bike(Vehicle):
    LONG_RENTAL_THRESHOLD_DAYS = 5
    LONG_RENTAL_DISCOUNT = 0.05

    def calculate_rental_cost(self, days: int) -> float:
        base_cost = self.daily_rate * days
        if days > self.LONG_RENTAL_THRESHOLD_DAYS:
            return base_cost * (1 - self.LONG_RENTAL_DISCOUNT)
        return base_cost
```
- `LONG_RENTAL_THRESHOLD_DAYS` and `LONG_RENTAL_DISCOUNT` are **class
  attributes** — shared constants attached to the class itself, not to
  any one instance. Using named constants instead of writing `5` and
  `0.05` directly in the formula makes the rule self-documenting and easy
  to tweak in one place.
- The logic: compute the plain cost first, then if `days` is more than 5,
  multiply by `(1 - 0.05)` = `0.95`, i.e. take 5% off. Otherwise return
  the full cost unchanged.

```python
class Van(Vehicle):
    def __init__(self, vehicle_id: str, registration_number: str,
                 brand: str, model: str, daily_rate: float,
                 service_charge: float = 500.0):
        super().__init__(vehicle_id, registration_number, brand, model, daily_rate)
        if service_charge < 0:
            raise ValidationError("Service charge cannot be negative.")
        self.__service_charge = float(service_charge)
```
- `Van` needs one extra piece of data (`service_charge`) that `Car` and
  `Bike` don't have, so unlike them, it **overrides `__init__` too**.
- `service_charge: float = 500.0` — a **default parameter**. If whoever
  creates a `Van` doesn't specify a service charge, it defaults to 500.
- `super().__init__(...)` calls the **parent class's** constructor first,
  passing along the five shared fields, so all that validation and
  private-field setup still happens exactly as it does for `Car`/`Bike`.
  Only *after* that do we validate and store the one extra field
  `Van` needs.
- `self.__service_charge` — note this is a *different* mangled name than
  anything on `Vehicle` (`_Van__service_charge` vs. `_Vehicle__...`), so
  there's no collision even though both classes use `__` prefixes.

```python
    def calculate_rental_cost(self, days: int) -> float:
        return (self.daily_rate * days) + self.__service_charge
```
- Same idea as `Car`, but adds the flat `service_charge` on top.

### The polymorphism moment (be ready to point to this exact idea)

Later, in `services/rental_service.py` and `models/rental.py`, you'll see
this line:
```python
base_amount = vehicle.calculate_rental_cost(days)
```
`vehicle` here is typed as `Vehicle`, but at runtime it's actually a
`Car`, `Bike`, or `Van` object. Because each subclass overrides
`calculate_rental_cost` with its own version, **Python automatically
runs the correct one** — this is called **dynamic dispatch**. The calling
code never needs to write `if vehicle_type == "Car": ... elif ...`. That
single line of code behaves three different ways depending on what kind
of object is behind it — that *is* polymorphism.

---

## 3. `models/customer.py`

```python
class Customer:
    def __init__(self, customer_id: str, name: str, email: str, licence_number: str):
```
- No `(ABC)` here — `Customer` is a normal, concrete class. There's only
  ever one "kind" of customer in this system, so there's no need for an
  abstract base or subclasses.

```python
        if not customer_id or not str(customer_id).strip():
            raise ValidationError("Customer ID cannot be empty.")
        if not name or not name.strip():
            raise ValidationError("Customer name cannot be empty.")
        if not email or "@" not in email:
            raise ValidationError("A valid email address is required.")
        if not licence_number or not licence_number.strip():
            raise ValidationError("Driving licence number cannot be empty.")
```
- Same empty-field validation pattern as `Vehicle`. The email check adds
  one extra rule: `"@" not in email` — a very simple sanity check (not a
  full email-format validator, just enough to catch obvious mistakes).

```python
        self.__customer_id = customer_id
        self.__name = name
        self.__email = email
        self.__licence_number = licence_number
        self.__rental_history = []  # list[Rental] -- association, populated over time
```
- Same private-field pattern. `__rental_history` starts as an **empty
  list** — a brand-new customer has rented nothing yet. This list will
  hold `Rental` *objects* later, not just IDs — that's what makes this an
  **association** between `Customer` and `Rental`.

```python
    @property
    def rental_history(self) -> list:
        # return a copy so external code cannot mutate internal state directly
        return list(self.__rental_history)
```
- `list(self.__rental_history)` creates a **new** list containing the
  same items. If we'd just returned `self.__rental_history` directly,
  outside code could call `.append()` or `.clear()` on the list we
  handed back and silently corrupt the customer's real history. Copying
  it closes that loophole — another small but deliberate encapsulation
  choice.

```python
    def add_rental(self, rental) -> None:
        self.__rental_history.append(rental)
```
- The **only** sanctioned way to add to a customer's history. Called by
  `RentalService.rent_vehicle()` right after a rental is successfully
  created (see §7 below).

```python
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
```
- If the list is empty, return a simple message immediately.
- Otherwise build up a list of text `lines`, one per rental, then join
  them all with newline characters (`"\n".join(...)`) into one big
  string to return. Building a list first and joining once at the end is
  more efficient than repeatedly concatenating strings with `+=` in a
  loop.
- Notice `rental.vehicle.vehicle_type` — this reaches from the `Rental`
  object, into the `Vehicle` object it's composed of, to read its type.
  That's only possible because `Rental` keeps a direct reference to the
  actual `Vehicle` object (see composition in §5).

---

## 4. `models/payment.py` — the interface

```python
class PaymentProcessor(ABC):
    """Interface every concrete payment method must implement."""

    @abstractmethod
    def process_payment(self, amount: float) -> "PaymentResult":
        raise NotImplementedError
```
- Same `ABC` + `@abstractmethod` pattern as `Vehicle`. But notice this
  class has **no `__init__`, no fields, no other methods** — just one
  abstract method. That's what makes it function as a pure **interface**
  (the Java/C# term) rather than a partial implementation to inherit
  from: it's 100% contract, 0% shared behaviour.
- `-> "PaymentResult"` — the return type is written in quotes because
  `PaymentResult` is defined *below* this class in the same file; quoting
  it as a string avoids a "not yet defined" error (this is called a
  forward reference).

```python
class PaymentResult:
    def __init__(self, method: str, masked_reference: str, amount: float, transaction_id: str):
        self.method = method
        self.masked_reference = masked_reference
        self.amount = amount
        self.transaction_id = transaction_id
```
- A plain **value object** — just carries data about a completed payment.
  Notice these fields are *not* double-underscored/private — this is a
  simple internal data holder, not something we need to protect from
  outside mutation, so the extra encapsulation ceremony isn't needed here.

```python
    def __str__(self):
        return (f"{self.method} payment of Rs. {self.amount:,.2f} succeeded "
                f"(ref: {self.masked_reference}, txn: {self.transaction_id})")
```
- Again, `__str__` controls what `print(payment_result)` shows.

```python
class CardPayment(PaymentProcessor):
    def __init__(self, card_number: str, card_holder_name: str):
        if not card_number or len(card_number.replace(" ", "")) < 12:
            raise ValidationError("A valid card number is required.")
```
- `card_number.replace(" ", "")` strips any spaces someone might type
  between digit groups (like `"4111 1111 1111 1234"`), then checks the
  cleaned-up string is at least 12 characters — a loose sanity check, not
  real card validation (a real payment gateway would do that).

```python
        digits = card_number.replace(" ", "")
        # Store only a masked reference -- never the full card number.
        self.__masked_number = f"**** **** **** {digits[-4:]}"
        self.__card_holder_name = card_holder_name
        self.__transaction_counter = 0
```
- `digits[-4:]` is **slicing**: it takes the last 4 characters of the
  string. So `"4111111111111234"[-4:]` gives `"1234"`.
- Critically: **the full `card_number` is never assigned to `self`
  anywhere.** Only the masked version is stored. This is what satisfies
  the assignment's rule that sensitive payment info must never be stored
  as plain text — the raw number exists only briefly as a local variable
  inside `__init__` and is discarded once the constructor returns.
- `__transaction_counter = 0` — starts a private counter used to generate
  unique transaction IDs each time this card object is used to pay.

```python
    def process_payment(self, amount: float) -> PaymentResult:
        if amount <= 0:
            raise PaymentFailedError("Payment amount must be greater than zero.")
        self.__transaction_counter += 1
        txn_id = f"CARD-TXN-{self.__transaction_counter:04d}"
        return PaymentResult("Card", self.__masked_number, amount, txn_id)
```
- This **overrides** the abstract method from `PaymentProcessor` —
  fulfilling the interface contract.
- `{self.__transaction_counter:04d}` — format spec `04d` means "format
  as a decimal integer, padded with leading zeros to 4 digits", so
  `1` becomes `"0001"`.
- Returns a `PaymentResult` object bundling everything the rest of the
  app needs to know about this successful payment.

`UpiPayment` follows the identical shape — validates the UPI ID contains
`"@"`, masks everything except the first character of the handle and the
provider (`"rohit@upi"` → `"r****@upi"`), and implements
`process_payment` the same way with a `UPI-TXN-####` id.

**Why the interface matters here:** `RentalService` (§7) only ever calls
`payment_processor.process_payment(amount)`. It never checks "is this a
`CardPayment` or `UpiPayment`?" — same polymorphism idea as `Vehicle`,
just applied to payments instead of vehicles. That's also **dependency
inversion**: the business logic depends on the abstract `PaymentProcessor`
contract, not on either concrete class.

---

## 5. `models/rental.py` — composition happens here

```python
LATE_FEE_RATE = 0.20  # 20% of daily rate, per late day
```
- A **module-level constant** (lives outside any class, so it belongs to
  the whole file). Written once here instead of hard-coded as `0.20`
  wherever it's used.

```python
class Rental:
    def __init__(self, rental_id: str, customer, vehicle, rental_days: int,
                 start_date: date = None):
```
- Notice `customer` and `vehicle` have **no type hint**. That's
  intentional — a `Rental` doesn't care about the specific `Customer` or
  `Vehicle` classes, only that whatever's passed in behaves the way it
  expects (has a `.name`, a `.calculate_rental_cost()`, etc.). This is
  sometimes called "duck typing."
- `start_date: date = None` — defaults to `None`, meaning "use today's
  date," handled a few lines down.

```python
        if not isinstance(rental_days, int) or rental_days <= 0:
            raise InvalidRentalDurationError("Rental days must be a whole number greater than zero.")
```
- `isinstance(rental_days, int)` checks the *type* is actually a whole
  number (not, say, a string or a float like `3.5`). Combined with the
  `<= 0` check, this is the one rule that directly enforces "rental days
  must be greater than zero" from the assignment.

```python
        self.__rental_id = rental_id
        self.__customer = customer
        self.__vehicle = vehicle
```
- **This is composition.** `self.__customer` and `self.__vehicle` are not
  copies of data — they are direct references to the actual `Customer`
  and `Vehicle` objects that were passed in. A `Rental` genuinely *has-a*
  `Customer` and *has-a* `Vehicle` inside it.

```python
        self.__rental_days = rental_days
        self.__start_date = start_date or date.today()
        self.__due_return_date = self.__start_date + timedelta(days=rental_days)
        self.__actual_return_date = None
        self.__status = "CONFIRMED"  # CONFIRMED -> RETURNED
        self.__payment_result = None
        self.__base_amount = vehicle.calculate_rental_cost(rental_days)
        self.__late_fee = 0.0
        self.__total_amount = self.__base_amount
```
- `start_date or date.today()` — if `start_date` was `None` (falsy),
  `or` falls through to `date.today()`. If a real date was passed, that's
  used instead.
- `date.today() + timedelta(days=rental_days)` — Python's `datetime`
  module lets you add a `timedelta` (a span of days) directly to a
  `date` to get another `date`. So a 3-day rental starting today gets a
  due date 3 days from now, automatically handling month/year rollovers.
- `self.__base_amount = vehicle.calculate_rental_cost(rental_days)` —
  **this is the polymorphism call** from §2, happening the moment a
  `Rental` is constructed. Whatever type `vehicle` actually is decides
  what number comes back here.
- `__status = "CONFIRMED"` — every new rental starts in this state; it
  only ever moves to `"RETURNED"`, never backwards.

```python
    @property
    def rental_id(self):
        return self.__rental_id
```
...and similarly for every other field. These properties are how
`Invoice`, `Customer.display_rental_history()`, and the CLI read a
rental's data without touching its private attributes directly — same
encapsulation pattern as `Vehicle`.

```python
    def attach_payment(self, payment_result) -> None:
        """Called by RentalService only after PaymentProcessor confirms success."""
        self.__payment_result = payment_result
```
- A separate method (not part of `__init__`) because payment happens
  *after* the `Rental` object exists but *before* it's considered fully
  confirmed — see the exact order of operations in `RentalService.rent_vehicle()`
  in §7.

```python
    def calculate_late_days(self, return_date: date) -> int:
        late_days = (return_date - self.__due_return_date).days
        return max(late_days, 0)
```
- Subtracting one `date` from another gives a `timedelta` object; `.days`
  extracts just the number of whole days as an integer. If returned early
  or exactly on time, this could be zero or negative.
- `max(late_days, 0)` clamps any negative number up to `0` — an early
  return should never produce a *negative* late fee.

```python
    def calculate_final_amount(self, return_date: date) -> float:
        late_days = self.calculate_late_days(return_date)
        self.__late_fee = late_days * LATE_FEE_RATE * self.__vehicle.daily_rate
        self.__total_amount = self.__base_amount + self.__late_fee
        return self.__total_amount
```
- This is the exact formula from the assignment: **late fee = number of
  late days × 20% of daily rate**. `LATE_FEE_RATE` is `0.20`, and
  `self.__vehicle.daily_rate` reaches into the composed `Vehicle` object
  to read its rate.
- `self.__total_amount = self.__base_amount + self.__late_fee` — final
  amount is always base + late fee (late fee is `0` if on time, so this
  formula works for both cases without a separate branch).

```python
    def complete_rental(self, return_date: date = None) -> None:
        return_date = return_date or date.today()
        self.__actual_return_date = return_date
        self.calculate_final_amount(return_date)
        self.__status = "RETURNED"
        self.__vehicle.mark_as_available()
```
- The method that actually finalizes a return. It records the return
  date, triggers the fee calculation above, flips the status, and —
  importantly — calls `mark_as_available()` on the composed `Vehicle`
  object, which is the **only** place in the whole system a returned
  vehicle becomes rentable again.

---

## 6. `models/invoice.py`

```python
class Invoice:
    def __init__(self, rental):
        self.__rental = rental
        self.__invoice_id = f"INV-{rental.rental_id}"
        self.__generated = False
        self.__body = ""
```
- An `Invoice` is composed of exactly one `Rental` — it can't exist
  without one, and it's built from that rental's own ID
  (`f"INV-{rental.rental_id}"` turns `"R0001"` into `"INV-R0001"`).
- `__generated` and `__body` start empty; they get filled in by
  `generate()` below, and this flag avoids re-doing the work twice.

```python
    def generate(self) -> str:
        r = self.__rental
        lines = [
            "=" * 50,
            f"INVOICE {self.__invoice_id}",
            "=" * 50,
            f"Customer        : {r.customer.name} ({r.customer.customer_id})",
            ...
        ]
```
- `r = self.__rental` — a short local alias just so the rest of the
  method doesn't have to repeatedly type `self.__rental`.
- `"=" * 50` — string multiplication: repeats the `"="` character 50
  times to build a divider line.
- `lines` is a Python **list** where each item becomes one printed line
  of the invoice; building it as a list first (rather than one giant
  string) makes it easy to conditionally add or skip lines, as seen next.

```python
        if r.actual_return_date:
            lines.append(f"Actual return   : {r.actual_return_date}")
```
- Only shows the "Actual return" line if the rental has actually been
  returned (`actual_return_date` is `None` until then) — so an invoice
  requested mid-rental doesn't show a false or missing return date line.

```python
        self.__body = "\n".join(lines)
        self.__generated = True
        return self.__body
```
- Joins every line in the list with a newline character between them
  into one big multi-line string, stores it, marks it generated, and
  returns it.

```python
    def display(self) -> None:
        if not self.__generated:
            self.generate()
        print(self.__body)
```
- A convenience wrapper: if nobody's called `generate()` yet, do it now,
  then print the result. This is what the CLI calls after a return.

---

## 7. `services/rental_service.py` — the business-rule layer

```python
class RentalService:
    def __init__(self):
        self.__vehicles = {}     # vehicle_id -> Vehicle
        self.__customers = {}    # customer_id -> Customer
        self.__rentals = {}      # rental_id -> Rental
        self.__invoices = {}     # rental_id -> Invoice
        self.__rental_counter = 0
```
- Four **dictionaries**, each keyed by an ID string, mapping to the
  actual object. Dictionaries give instant lookup by ID (`self.__vehicles["V101"]`)
  instead of having to search through a list every time.
- `__rental_counter` is used to auto-generate the next rental ID.

```python
    def add_vehicle(self, vehicle) -> None:
        if vehicle.vehicle_id in self.__vehicles:
            raise ValidationError(f"A vehicle with ID {vehicle.vehicle_id} already exists.")
        self.__vehicles[vehicle.vehicle_id] = vehicle
```
- `vehicle.vehicle_id in self.__vehicles` checks if that key already
  exists in the dictionary before allowing the add — stops two different
  vehicles from silently overwriting each other under the same ID.

```python
    def get_customer(self, customer_id: str):
        return self.__customers.get(customer_id)
```
- `.get(key)` on a dictionary returns `None` if the key isn't found,
  instead of raising an error the way `self.__customers[key]` would.
  That's deliberate here — the CLI checks `if not customer:` afterward
  and shows a friendly message rather than crashing.

```python
    def get_invoice(self, rental_id: str) -> Invoice:
        invoice = self.__invoices.get(rental_id)
        if not invoice:
            raise RentalNotFoundError(
                f"No invoice available for {rental_id} yet (vehicle may not be returned)."
            )
        return invoice
```
- Here, unlike `get_customer`, a missing invoice *does* raise an
  exception — because the CLI's "View invoice" option has nothing
  sensible to do except show an error if there's no invoice yet.

```python
    def search_vehicles(self, vehicle_id: str = None, vehicle_type: str = None,
                         min_price: float = None, max_price: float = None):
        if vehicle_id is not None:
            return self._search_by_id(vehicle_id)
        if vehicle_type is not None:
            return self._search_by_type(vehicle_type)
        if min_price is not None or max_price is not None:
            return self._search_by_price_range(min_price or 0, max_price or float("inf"))
        return list(self.__vehicles.values())
```
- This is the **method-overloading-style dispatch** — one public method
  with several optional parameters (all default to `None`), which checks
  which one(s) were actually supplied and routes to the matching private
  helper. If none are given at all, it just returns every vehicle.
- `min_price or 0` and `max_price or float("inf")` — if only one bound
  was given, fill in a sensible default for the other (`0` for no lower
  bound, infinity for no upper bound) so the range check still works.

```python
    def _search_by_id(self, vehicle_id: str):
        vehicle = self.__vehicles.get(vehicle_id)
        return [vehicle] if vehicle else []
```
- The leading underscore (`_search_by_id`, single underscore this time,
  not double) is a Python convention meaning "internal helper, not part
  of the public API" — a softer signal than the double-underscore name
  mangling used for fields.
- Returns a list with one item (or an empty list), so the return *shape*
  is consistent with the other two search helpers, which naturally
  return lists of possibly-many matches.

```python
    def _search_by_type(self, vehicle_type: str):
        return [v for v in self.__vehicles.values()
                if v.vehicle_type.lower() == vehicle_type.lower()]
```
- A **list comprehension**: reads as "give me `v` for every `v` in
  `self.__vehicles.values()`, but only if the condition after `if` is
  true." `.lower()` on both sides makes the comparison
  case-insensitive, so typing `"bike"`, `"Bike"`, or `"BIKE"` all match.

```python
    def _search_by_price_range(self, min_price: float, max_price: float):
        return [v for v in self.__vehicles.values()
                if min_price <= v.daily_rate <= max_price]
```
- `min_price <= v.daily_rate <= max_price` is a **chained comparison** —
  Python lets you write it this way instead of
  `min_price <= v.daily_rate and v.daily_rate <= max_price`.

```python
    def rent_vehicle(self, customer, vehicle_id: str, days: int,
                      payment_processor: PaymentProcessor) -> Rental:
```
- This is the single most important method in the whole project — it's
  where every business rule from the assignment comes together in the
  exact order they must be checked.

```python
        matches = self._search_by_id(vehicle_id)
        if not matches:
            raise VehicleNotFoundError(f"No vehicle found with ID {vehicle_id}.")
        vehicle = matches[0]
```
- Step 1: does this vehicle exist at all? If `matches` is an empty list,
  `not matches` is `True`, so we raise before going any further.
  `matches[0]` grabs the one match out of the list `_search_by_id`
  returns.

```python
        if not vehicle.is_available:
            raise VehicleUnavailableError(
                f"Vehicle {vehicle.vehicle_id} ({vehicle.vehicle_type}) is currently unavailable."
            )
```
- Step 2: is it currently available? This is the exact check that stops
  "Customer B tries to rent the same car" from the mandatory scenario.

```python
        if not isinstance(days, int) or days <= 0:
            raise InvalidRentalDurationError("Rental duration must be a positive whole number of days.")
```
- Step 3: is the requested duration valid? Same rule enforced again here
  (in addition to inside `Rental.__init__`) so we fail *before* touching
  payment or state at all — belt-and-suspenders validation.

```python
        provisional_amount = vehicle.calculate_rental_cost(days)

        try:
            payment_result = payment_processor.process_payment(provisional_amount)
        except PaymentFailedError:
            raise  # re-raise; rental is never created if payment fails
```
- Step 4: **compute the cost, then attempt payment, before creating
  anything.** `provisional_amount` uses the same polymorphic
  `calculate_rental_cost` call from §2/§5.
- `try / except PaymentFailedError: raise` — this `except` block
  catches the error only to immediately `raise` it again unchanged. Why
  write it at all? It documents, right at this exact spot in the code,
  that a payment failure here is expected and deliberately stops
  everything below from running — nothing after this block executes if
  payment fails, so the vehicle and rental records are never touched.

```python
        self.__rental_counter += 1
        rental_id = f"R{self.__rental_counter:04d}"
        rental = Rental(rental_id, customer, vehicle, days)
        rental.attach_payment(payment_result)

        vehicle.mark_as_rented()
        customer.add_rental(rental)
        self.__rentals[rental_id] = rental

        return rental
```
- Only once payment has succeeded do we reach this point. In order:
  1. Generate the next rental ID (`R0001`, `R0002`, ...).
  2. Construct the `Rental` object (composing the customer, vehicle, and
     days together — this also runs the days validation and cost
     calculation again inside `Rental.__init__`).
  3. Attach the payment result we already collected.
  4. Flip the vehicle to unavailable.
  5. Add this rental to the customer's history.
  6. Store the rental in the service's own dictionary so it can be found
     later by ID (for returning it, viewing its invoice, etc.).
- This exact ordering is what guarantees "payment must complete
  successfully before the rental is confirmed" from the assignment.

```python
    def return_vehicle(self, rental_id: str, return_date: date = None) -> Invoice:
        rental = self.__rentals.get(rental_id)
        if not rental:
            raise RentalNotFoundError(f"No active rental found with ID {rental_id}.")

        rental.complete_rental(return_date or date.today())
        invoice = Invoice(rental)
        invoice.generate()
        self.__invoices[rental_id] = invoice
        return invoice
```
- Look up the rental; if it doesn't exist, fail immediately.
- `rental.complete_rental(...)` does all the heavy lifting (late fee,
  status change, marking the vehicle available again) — that logic lives
  on `Rental` itself, not duplicated here (single responsibility).
- Then build and generate an `Invoice` from that now-completed rental,
  save it for later lookup, and hand it back to the caller.

---

## 8. `cli/console_io.py` — input helpers

```python
def prompt_str(label: str, allow_empty: bool = False) -> str:
    while True:
        value = input(f"{label}: ").strip()
        if value or allow_empty:
            return value
        print("  This field can't be empty. Please try again.")
```
- `while True:` starts an infinite loop that only ends via `return`
  inside it — the function keeps asking until it gets something
  acceptable.
- `input(f"{label}: ")` prints the label as a prompt and waits for the
  user to type something and press Enter; whatever they typed comes back
  as a string.
- `.strip()` removes accidental leading/trailing spaces.
- `if value or allow_empty:` — if the user typed something (`value` is a
  non-empty string, which is truthy), OR the caller explicitly said empty
  is fine, return it. Otherwise print an error and the `while True` loop
  goes around again.

```python
def prompt_int(label: str, min_value: int = None) -> int:
    while True:
        raw = input(f"{label}: ").strip()
        try:
            value = int(raw)
        except ValueError:
            print("  Please enter a whole number.")
            continue
        if min_value is not None and value < min_value:
            print(f"  Please enter a number of at least {min_value}.")
            continue
        return value
```
- `int(raw)` tries to convert the typed text to a whole number. If the
  user typed `"abc"`, this raises a `ValueError`, which we catch and turn
  into a friendly message.
- `continue` jumps straight back to the top of the `while True:` loop,
  skipping the rest of the function body and asking again.
- `min_value is not None and value < min_value` — only enforces a
  minimum if the caller actually specified one (some callers don't need
  a lower bound at all).

`prompt_float` is the same idea using `float(raw)` instead of `int(raw)`.

```python
def prompt_choice(label: str, valid_choices) -> str:
    valid_choices = [str(c) for c in valid_choices]
    while True:
        value = input(f"{label} [{'/'.join(valid_choices)}]: ").strip()
        if value in valid_choices:
            return value
        print(f"  Invalid choice. Please enter one of: {', '.join(valid_choices)}")
```
- `[str(c) for c in valid_choices]` — a list comprehension that converts
  every choice to a string (so it works whether you pass in `["1","2"]`
  or `[1, 2]`).
- `'/'.join(valid_choices)` turns `["1","2","3"]` into `"1/2/3"` to show
  in the prompt, e.g. `Enter your choice [1/2/3]:`.
- `if value in valid_choices:` — checks the typed value is exactly one of
  the allowed options before accepting it.

```python
def prompt_yes_no(label: str) -> bool:
    value = prompt_choice(f"{label} (y/n)", ["y", "n", "Y", "N"])
    return value.lower() == "y"
```
- Reuses `prompt_choice` instead of writing separate validation —
  accepts either case, then normalizes with `.lower()` before comparing.

```python
def pause():
    input("\nPress Enter to return to the menu...")
```
- `input()` here ignores whatever's typed — it's used purely to make the
  program wait for the user to press Enter before clearing on to the
  next menu screen, so they have time to read the output first.

---

## 9. `cli/app.py` — the interactive menu

```python
class RentalApp:
    def __init__(self):
        self.service = RentalService()
        self._seed_initial_data()
```
- `RentalApp` owns exactly one `RentalService` instance, created fresh
  every time the app starts. `_seed_initial_data()` is called immediately
  so there's inventory to look at right away.

```python
    def _seed_initial_data(self):
        self.service.add_vehicle(Car("V101", "KA01AB1234", "Toyota", "Etios", 2000))
        self.service.add_vehicle(Bike("V102", "KA01CD5678", "Yamaha", "FZ", 700))
        self.service.add_vehicle(Van("V103", "KA01EF9012", "Tata", "Winger", 3000, service_charge=500))
```
- Creates one of each vehicle type and adds them through the service's
  public `add_vehicle` method (never touching `RentalService`'s private
  dictionary directly) — matches the assignment's sample vehicles.

```python
    MENU_TEXT = """
==================================================
        VEHICLE RENTAL MANAGEMENT SYSTEM
==================================================
 1. View available vehicles
 ...
"""
```
- A **class attribute** holding a multi-line string (triple quotes
  `"""..."""` let a string span several lines exactly as written,
  including the blank lines and spacing).

```python
    def run(self):
        print("Welcome to the Vehicle Rental Management System.")
        print("Starting inventory has been loaded (1 Car, 1 Bike, 1 Van).")
        while True:
            print(self.MENU_TEXT)
            choice = prompt_choice("Enter your choice", [str(i) for i in range(1, 10)])
            if choice == "9":
                print("\nThank you for using the Vehicle Rental Management System. Goodbye!")
                break
```
- `[str(i) for i in range(1, 10)]` generates `["1","2",...,"9"]` — the
  valid menu numbers — without typing them out by hand.
- `while True:` is the **main menu loop**: print the menu, wait for a
  valid choice, and keep going forever until the user picks `9`, which
  triggers `break` to exit the loop (and the method).

```python
            handler = self.HANDLERS[choice]
            try:
                handler(self)
            except RentalSystemError as e:
                print(f"\n[Error] {e}")
            pause()
```
- `self.HANDLERS` is a **dictionary that maps menu numbers to methods**
  (defined at the very bottom of the class — see below). `handler` ends
  up being the actual function object for whichever option was chosen.
- `handler(self)` calls it, explicitly passing `self` because these
  functions are stored as *plain* functions in the dictionary, not
  bound methods — Python needs `self` handed to them manually here.
- `except RentalSystemError as e:` — this single `except` catches
  **every** custom exception in the whole project (because they all
  inherit from `RentalSystemError`, as explained in §1), and `{e}` in
  the f-string automatically shows the message that was passed to
  `raise SomeError("...")`.
- `pause()` runs after every action (success or failure) so the user has
  a moment to read the result before the screen refreshes with the menu.

```python
    def handle_rent_vehicle(self):
        print("\nRent a vehicle")
        customer = self._get_or_register_customer()
        if customer is None:
            return
```
- Calls a shared helper (below) to get a valid `Customer` object,
  registering a new one on the fly if needed. If that process didn't
  produce a usable customer, `return` exits this handler early — back to
  the main menu loop.

```python
        matches = self.service.search_vehicles(vehicle_id=vehicle_id)
        if not matches:
            print(f"  No vehicle found with ID {vehicle_id}.")
            return
        if not matches[0].is_available:
            print(f"  Vehicle {vehicle_id} ({matches[0].vehicle_type}) is currently unavailable.")
            return
```
- This is a **pre-check done in the CLI itself**, before ever asking for
  payment details — so if you try to rent an already-rented car, you get
  told immediately instead of being asked for your card number first and
  finding out only after. (`RentalService.rent_vehicle` would also catch
  this and raise `VehicleUnavailableError` — this is a belt-and-suspenders
  UX improvement, not a replacement for that check.)

```python
        days = prompt_int("Enter rental duration in days", min_value=1)
        payment_processor = self._collect_payment_method()

        rental = self.service.rent_vehicle(customer, vehicle_id, days, payment_processor)
```
- Only once the vehicle's confirmed available does the code ask for
  rental days and payment info, then finally calls into the service
  layer to actually perform the rental.

```python
    def _get_or_register_customer(self):
        customer_id = prompt_str("Enter your customer ID (or leave blank to register as new)",
                                  allow_empty=True)
        if not customer_id:
            print("\nLet's register you as a new customer first.")
            self.handle_register_customer()
            customer_id = prompt_str("Now enter the customer ID you just created")
```
- `allow_empty=True` lets someone just press Enter with nothing typed —
  `if not customer_id:` then treats that as "I'm new, register me,"
  reusing `handle_register_customer()` rather than duplicating that
  logic.

```python
    def _collect_payment_method(self):
        print("\nChoose a payment method:")
        print(" 1. Card")
        print(" 2. UPI")
        method = prompt_choice("Enter choice", ["1", "2"])

        if method == "1":
            card_number = prompt_str("Enter card number")
            card_holder_name = prompt_str("Enter name on card")
            return CardPayment(card_number, card_holder_name)
        else:
            upi_id = prompt_str("Enter UPI ID (e.g. name@bank)")
            return UpiPayment(upi_id)
```
- Depending on the choice, constructs and returns either a `CardPayment`
  or `UpiPayment` object — but the *return type* from the caller's
  perspective is just "some `PaymentProcessor`". This is the exact
  moment the concrete class gets chosen; everything downstream
  (`RentalService.rent_vehicle`) only ever sees it through the interface.

```python
    HANDLERS = {
        "1": handle_view_available,
        "2": handle_search,
        "3": handle_register_customer,
        "4": handle_rent_vehicle,
        "5": handle_return_vehicle,
        "6": handle_view_invoice,
        "7": handle_view_history,
        "8": handle_add_vehicle,
    }
```
- Placed at the very bottom of the class body, after every handler
  method has already been defined above it, so each name (like
  `handle_view_available`) refers to the actual function object at the
  point this dictionary is built. This is what `run()`'s
  `self.HANDLERS[choice]` looks up.

### How every handler logs its own outcome

```python
self.logger.log(
    action="rent_vehicle",
    status="success",
    details={
        "rental_id": rental.rental_id,
        "customer_id": customer.customer_id,
        ...
    },
)
```
- Every handler calls `self.logger.log(...)` at each point where
  something worth recording just happened — not just on success, but
  also on a **blocked** attempt (renting an unavailable vehicle, a
  duplicate customer ID) with `status="blocked"` and a `reason` field in
  `details` explaining why. This is a deliberate design choice: a blocked
  double-booking attempt is just as informative a record as a successful
  rental, so it gets logged too, not silently dropped.
- Genuine exceptions are logged in exactly one place — `run()`'s
  `except RentalSystemError as e:` block — using
  `self.ACTION_NAMES.get(choice, "unknown")` to recover which menu option
  was active, since the handler itself never got the chance to log
  anything before the exception unwound out of it.

---

## 10. `cli/activity_log.py` — the JSON activity log

```python
DEFAULT_LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "activity_log.json",
)
```
- Builds an absolute path to `data/activity_log.json` **relative to this
  file's own location** (`os.path.abspath(__file__)` is the full path to
  `activity_log.py` itself; `os.path.dirname` twice walks up from
  `cli/activity_log.py` to `cli/` and then to the project root). This
  means the log always lands in the same place no matter what folder you
  happen to run `python main.py` from.

```python
def _json_safe(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value
```
- Python's `json` module doesn't know how to serialize a `date` object
  (like `rental.due_return_date`) on its own — calling `json.dump()` on
  a dictionary containing one would raise a `TypeError`. This function
  walks recursively into dicts and lists and converts any `date`/
  `datetime` it finds into a plain string via `.isoformat()` (e.g.
  `date(2026, 9, 7)` becomes `"2026-09-07"`), so any handler can log a
  dictionary containing raw domain objects without needing to convert
  dates itself first.
- "Recursively" matters here because `details` dictionaries often
  contain **nested** lists of dictionaries (e.g. `view_available_vehicles`
  logs a list of vehicle summary dicts) — a shallow conversion would miss
  dates buried inside those.

```python
class ActivityLogger:
    def __init__(self, path: str = DEFAULT_LOG_PATH):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            self._write([])
```
- `os.makedirs(..., exist_ok=True)` creates the `data/` folder if it
  doesn't exist yet, and does nothing (no error) if it already does.
- If the log file itself doesn't exist yet, it's initialized with an
  empty JSON array `[]` — a valid, parseable starting point. Note this
  only happens if the file is **missing entirely**; an existing file
  from a previous run is left untouched.

```python
    def log(self, action: str, status: str, details: dict) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "action": action,
            "status": status,
            "details": _json_safe(details),
        }
        records = self._read()
        records.append(entry)
        self._write(records)
```
- This is the only method the rest of the app calls. It builds one
  `entry` dictionary, timestamped to the second, then does a
  **read-modify-write**: read the whole existing list of past entries,
  append the new one in memory, and write the whole list back out.
- This approach trades a small amount of inefficiency (rewriting the
  entire file on every single action) for a big usability win: the file
  is always a single, valid, complete JSON array that any JSON viewer or
  `json.load()` call can open directly — no special line-by-line parsing
  needed, unlike the JSON Lines format some logging systems use.

```python
    def _read(self) -> list:
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
```
- Defensive: if the file got deleted or corrupted between runs (or by
  someone hand-editing it and leaving invalid JSON), this falls back to
  starting from an empty list rather than crashing the whole
  application over a logging problem.

---

## 11. `main.py`

```python
from cli import RentalApp

def main():
    app = RentalApp()
    app.run()

if __name__ == "__main__":
    main()
```
- `from cli import RentalApp` — imports the class from the `cli` package
  (Python resolves this via `cli/__init__.py`, which re-exports it).
- `def main():` wraps the startup logic in its own function rather than
  writing it directly at the bottom of the file — a common Python
  convention that keeps things tidy and testable.
- `if __name__ == "__main__":` — this is Python's standard way of saying
  "only run `main()` if this file was executed directly (`python
  main.py`), not if it was imported by some other file." Since
  `main.py` is never meant to be imported elsewhere, this mostly matters
  as a widely-recognized convention.

---

## 12. Quick answers if you get asked "why...?"

- **Why private fields everywhere (`__field`)?** So state can only
  change through methods that validate it — nobody outside the class can
  set a negative daily rate or silently corrupt rental history.
- **Why is `Vehicle` abstract instead of a normal class?** Because no
  generic "vehicle" is ever rented in real life — every real instance is
  a Car, Bike, or Van, each with its own pricing rule. Making it abstract
  stops anyone from creating a vehicle object with no defined cost
  formula.
- **Why does `PaymentProcessor` have no shared code, just one abstract
  method?** Because it's meant to be a pure interface/contract — `Card`
  and `UPI` payments don't actually share any implementation, only the
  same method signature.
- **Why does the CLI never touch `self.__vehicles` or private fields
  directly?** Because `cli/app.py` only imports and calls public methods
  on `RentalService` and the model classes — that's what makes it
  possible to swap the terminal menu for a completely different
  interface later without touching business logic at all.
- **Why one `except RentalSystemError` instead of six separate excepts?**
  Because every custom exception inherits from that one base class, so
  catching the base class catches all of them — see §1.
- **What would you change to support a fourth vehicle type, say Truck?**
  Add one new class `Truck(Vehicle)` implementing
  `calculate_rental_cost()`. Nothing in `RentalService`, `Rental`,
  `Invoice`, or `cli/app.py` needs to change — that's the payoff of
  polymorphism plus depending on the `Vehicle` abstraction everywhere.
- **Why log to a JSON file instead of, say, a database?** For a
  single-user console app, a JSON file is simpler to set up (no extra
  dependency or server), trivially readable by both humans and other
  programs, and more than fast enough at the pace a person can type menu
  choices. A database would make sense if this grew into a
  multi-user, concurrent system.

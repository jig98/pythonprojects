"""
invoice.py

Invoice takes a completed Rental and turns it into a formatted breakdown.
Keeping this separate from Rental follows single-responsibility: Rental
owns the business state and math, Invoice owns presentation.
"""


class Invoice:
    def __init__(self, rental):
        self.__rental = rental
        self.__invoice_id = f"INV-{rental.rental_id}"
        self.__generated = False
        self.__body = ""

    @property
    def invoice_id(self):
        return self.__invoice_id

    def generate(self) -> str:
        r = self.__rental
        lines = [
            "=" * 50,
            f"INVOICE {self.__invoice_id}",
            "=" * 50,
            f"Customer        : {r.customer.name} ({r.customer.customer_id})",
            f"Vehicle         : {r.vehicle.vehicle_type} - {r.vehicle.brand} {r.vehicle.model} "
            f"({r.vehicle.registration_number})",
            f"Rental duration : {r.rental_days} day(s)",
            f"Start date      : {r.start_date}",
            f"Due return date : {r.due_return_date}",
        ]
        if r.actual_return_date:
            lines.append(f"Actual return   : {r.actual_return_date}")
        lines += [
            "-" * 50,
            f"Base rental amount : Rs. {r.base_amount:,.2f}",
            f"Late fee           : Rs. {r.late_fee:,.2f}",
            f"Final amount       : Rs. {r.total_amount:,.2f}",
        ]
        if r.payment_result:
            lines.append(f"Payment            : {r.payment_result}")
        lines.append("=" * 50)

        self.__body = "\n".join(lines)
        self.__generated = True
        return self.__body

    def display(self) -> None:
        if not self.__generated:
            self.generate()
        print(self.__body)

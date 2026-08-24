"""
employee_processor.py

Implements the core advanced-Python building blocks used by this project:
    - EmployeeIterator   (Iterator)
    - employee_generator (Generator)
    - filter_by_department (Generator)
    - create_salary_filter (Closure)
    - log_execution      (Decorator)
"""

import functools


# ---------------------------------------------------------------------------
# Requirement 1 — Iterator
# ---------------------------------------------------------------------------
class EmployeeIterator:
    """
    A custom iterator that walks through a list of employee records
    one at a time, using the standard iterator protocol
    (__iter__ / __next__).
    """

    def __init__(self, employees):
        self.employees = employees
        self.index = 0

    def __iter__(self):
        # An iterator must return itself from __iter__.
        return self

    def __next__(self):
        if self.index >= len(self.employees):
            raise StopIteration
        employee = self.employees[self.index]
        self.index += 1
        return employee


# ---------------------------------------------------------------------------
# Requirement 2 — Generator
# ---------------------------------------------------------------------------
def employee_generator(employees):
    """
    A generator function that yields employees one at a time,
    lazily, instead of building a whole list in memory.
    """
    for employee in employees:
        yield employee


def filter_by_department(employees, department):
    """
    A generator function that yields only the employees who
    belong to the requested department.
    """
    for employee in employees:
        if employee["department"] == department:
            yield employee


# ---------------------------------------------------------------------------
# Requirement 3 — Closure
# ---------------------------------------------------------------------------
def create_salary_filter(min_salary):
    """
    Returns a function `check` that "remembers" min_salary via a closure,
    even after create_salary_filter() itself has finished executing.
    """

    def check(employee):
        return employee["salary"] >= min_salary

    return check


# ---------------------------------------------------------------------------
# Requirement 4 — Decorator
# ---------------------------------------------------------------------------
def log_execution(func):
    """
    A decorator that logs when the wrapped function starts and finishes,
    without changing the function's own implementation.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[START] {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[END] {func.__name__}")
        return result

    return wrapper

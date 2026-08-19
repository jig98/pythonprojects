"""
salary.py

Simple salary and bonus calculations for an employee.
"""

TAX_RATE = 0.05     # flat 5% tax used for net salary calculation
BONUS_RATE = 0.10   # default 10% bonus rate


def calculate_salary(base_salary, deductions=0):
    """
    Return the net salary after a flat tax and any extra deductions.

    base_salary: the employee's gross salary
    deductions:  any additional deductions (e.g. loans, leave without pay)
    """
    tax = base_salary * TAX_RATE
    net_salary = base_salary - tax - deductions
    return round(net_salary, 2)


def calculate_bonus(base_salary, rate=BONUS_RATE):
    """Return the bonus amount for a given base salary and bonus rate."""
    return round(base_salary * rate, 2)

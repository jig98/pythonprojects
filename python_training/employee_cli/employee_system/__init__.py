"""
employee_system package

Groups the employee, salary, and attendance modules together so they
can be imported as:

    from employee_system.employee import get_all_employees
    from employee_system.salary import calculate_salary
    from employee_system.attendance import mark_attendance

The presence of this __init__.py file is what turns the
employee_system/ folder into a Python package (as opposed to just a
plain folder of scripts).
"""

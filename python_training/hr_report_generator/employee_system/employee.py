"""
employee.py

Handles storage and retrieval of employee records.
Uses a simple in-memory list of dictionaries (no database required).
"""

employees = [
    {"id": "E001", "name": "John", "department": "IT", "salary": 50000},
    {"id": "E002", "name": "Alice", "department": "HR", "salary": 45000},
    {"id": "E003", "name": "Bob", "department": "Finance", "salary": 55000},
]


def add_employee(emp_id, name, department, salary):
    """Add a new employee record and return it."""
    employee = {
        "id": emp_id,
        "name": name,
        "department": department,
        "salary": salary,
    }
    employees.append(employee)
    return employee


def get_employee(emp_id):
    """Return the employee dict matching emp_id, or None if not found."""
    for emp in employees:
        if emp["id"] == emp_id:
            return emp
    return None


def get_all_employees():
    """Return the full list of employee records."""
    return employees

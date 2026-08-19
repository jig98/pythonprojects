"""
HR Report Generator
====================
Generates a per-employee text report from a Jinja2 template, and
displays all employees in a formatted ASCII table using PrettyTable.

Run with the project's virtual environment active:
    python app.py
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from prettytable import PrettyTable

from employee_system.employee import get_all_employees
from employee_system.salary import calculate_salary, calculate_bonus

TEMPLATE_DIR = Path(__file__).parent / "templates"


def generate_report(employee):
    """Render a single employee's report using the Jinja2 template."""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("employee_report.txt")
    return template.render(employee=employee)


def build_employee_table(employees):
    """Build a PrettyTable containing all employee records."""
    table = PrettyTable()
    table.field_names = ["ID", "Name", "Department", "Salary"]
    for emp in employees:
        table.add_row([emp["id"], emp["name"], emp["department"], emp["salary"]])
    return table


def main():
    employees = get_all_employees()

    print("=" * 40)
    print(" HR EMPLOYEE REPORT")
    print("=" * 40)

    # --- Jinja2: one rendered report per employee ---
    for emp in employees:
        print(generate_report(emp))

    # --- PrettyTable: all employees in one table ---
    print("Employee Table")
    print("=" * 14)
    print(build_employee_table(employees))

    # --- salary.py demonstration ---
    print("\nSalary / Bonus Summary")
    print("=" * 23)
    for emp in employees:
        net = calculate_salary(emp["salary"])
        bonus = calculate_bonus(emp["salary"])
        print(f"{emp['name']:<8} Net Salary: {net:<10} Bonus: {bonus}")


if __name__ == "__main__":
    main()

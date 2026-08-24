"""
main.py

Entry point that demonstrates every requirement of the assignment:
    1. Iterator
    2. Generator
    3. Closure
    4. Decorator
    5. Context Manager
    6. Final combined report (generate_employee_report)
    7. Bonus — interactive report generation
"""

from employee_processor import (
    EmployeeIterator,
    employee_generator,
    filter_by_department,
    create_salary_filter,
    log_execution,
)
from report import generate_employee_report


employees = [
    {"id": 101, "name": "John", "department": "IT", "salary": 50000},
    {"id": 102, "name": "Mary", "department": "HR", "salary": 45000},
    {"id": 103, "name": "David", "department": "IT", "salary": 65000},
    {"id": 104, "name": "Sarah", "department": "Finance", "salary": 55000},
    {"id": 105, "name": "Alex", "department": "IT", "salary": 75000},
    {"id": 106, "name": "Lisa", "department": "HR", "salary": 48000},
]


# --- extra @log_execution examples (Requirement 4 asks for at least two) ---
@log_execution
def generate_report():
    print("Generating employee report...")


@log_execution
def calculate_average_salary(employee_list):
    total = sum(e["salary"] for e in employee_list)
    average = total / len(employee_list)
    print(f"Average salary: {average:.2f}")
    return average


def demo_iterator():
    print("\n--- Requirement 1: Iterator ---")
    iterator = EmployeeIterator(employees)
    print(next(iterator)["name"])
    print(next(iterator)["name"])
    print(next(iterator)["name"])


def demo_generator():
    print("\n--- Requirement 2: Generator ---")
    for employee in employee_generator(employees):
        print(employee["name"])

    print("\nFilter by department (IT):")
    for employee in filter_by_department(employees, "IT"):
        print(employee["name"])


def demo_closure():
    print("\n--- Requirement 3: Closure ---")
    high_salary = create_salary_filter(60000)
    print(high_salary(employees[0]))  # John  -> 50000 -> False
    print(high_salary(employees[2]))  # David -> 65000 -> True


def demo_decorator():
    print("\n--- Requirement 4: Decorator ---")
    generate_report()
    calculate_average_salary(employees)


def demo_combined():
    print("\n--- Final Requirement: Combined Report (IT, min 60000) ---")
    generate_employee_report(employees, "IT", 60000)


def bonus_interactive():
    print("\n--- Bonus Challenge: Interactive Report ---")
    department = input("Enter department: ").strip()
    min_salary_raw = input("Enter minimum salary: ").strip()
    try:
        min_salary = float(min_salary_raw)
    except ValueError:
        print("Invalid salary entered, defaulting to 0.")
        min_salary = 0

    print("Generating report...")
    generate_employee_report(employees, department, min_salary)


if __name__ == "__main__":
    demo_iterator()
    demo_generator()
    demo_closure()
    demo_decorator()
    demo_combined()

    try:
        run_bonus = input("\nRun bonus interactive report? (y/n): ").strip().lower()
    except EOFError:
        run_bonus = "n"

    if run_bonus == "y":
        bonus_interactive()

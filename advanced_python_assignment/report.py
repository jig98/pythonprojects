"""
report.py

Implements:
    - ReportFile (Requirement 5 — Context Manager)
    - generate_employee_report (Final Requirement — combines everything)
"""

from employee_processor import (
    employee_generator,
    filter_by_department,
    create_salary_filter,
    log_execution,
)


# ---------------------------------------------------------------------------
# Requirement 5 — Context Manager
# ---------------------------------------------------------------------------
class ReportFile:
    """
    A custom context manager that opens a file in __enter__ and
    guarantees it is closed in __exit__, even if an error occurs
    while writing.
    """

    def __init__(self, filename, mode="w"):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        # Returning False (or None) lets any exception propagate normally.
        return False


# ---------------------------------------------------------------------------
# Final Requirement — Combine everything
# ---------------------------------------------------------------------------
@log_execution
def generate_employee_report(employees, department, min_salary, filename="employee_report.txt"):
    """
    Ties together every concept from the assignment:

        Employee List -> Generator -> Filter by Department -> Closure
        -> Filter by Salary -> Context Manager -> Write Report
        (the whole call is wrapped by @log_execution)
    """
    # 1. Generator: stream the raw employee list lazily.
    all_employees = employee_generator(employees)

    # 2. Generator: filter that stream down to one department.
    dept_employees = filter_by_department(all_employees, department)

    # 3. Closure: build a reusable "is salary high enough" check.
    salary_ok = create_salary_filter(min_salary)
    filtered_employees = [emp for emp in dept_employees if salary_ok(emp)]

    # 4. Context Manager: write the report, guaranteeing the file closes.
    with ReportFile(filename) as report:
        report.write("Employee Report\n")
        report.write("===============\n")
        report.write(f"Department: {department}\n")
        report.write(f"Minimum Salary: {min_salary}\n\n")
        for emp in filtered_employees:
            report.write(
                f"{emp['id']} - {emp['name']} - {emp['department']} - {emp['salary']}\n"
            )

    print(f"Report saved successfully to '{filename}'.")
    return filtered_employees

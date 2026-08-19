"""
Employee CLI Application
=========================
Displays employee information directly in the terminal using two
different libraries: Tabulate (simple CLI tables) and Rich
(styled terminal tables).

Run with the project's virtual environment active:
    python app.py
"""

from tabulate import tabulate
from rich.console import Console
from rich.table import Table

from employee_system.employee import get_all_employees


def show_tabulate_table(employees, fmt="grid"):
    """Print employee data using tabulate with the given table format."""
    heading = f"Employee List - Tabulate ({fmt})"
    print(heading)
    print("-" * len(heading))
    print(tabulate(employees, headers="keys", tablefmt=fmt))


def show_rich_table(employees):
    """Print employee data using a styled Rich table."""
    console = Console()
    table = Table(title="Employee Details")

    # Column styling + alignment
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Department", style="green")
    table.add_column("Salary", justify="right", style="yellow")

    for emp in employees:
        table.add_row(emp["id"], emp["name"], emp["department"], str(emp["salary"]))

    console.print(table)


def main():
    employees = get_all_employees()

    print("=" * 40)
    print(" EMPLOYEE CLI APPLICATION")
    print("=" * 40)

    # --- Tabulate: experiment with two formats ---
    show_tabulate_table(employees, fmt="grid")
    print()
    show_tabulate_table(employees, fmt="simple")

    # --- Rich: styled terminal table ---
    print("\nEmployee List - Rich")
    print("-" * 20)
    show_rich_table(employees)


if __name__ == "__main__":
    main()

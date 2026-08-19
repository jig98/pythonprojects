"""
attendance.py

Simple in-memory attendance tracking for employees.
"""

# {emp_id: [{"date": "2026-08-01", "status": "Present"}, ...]}
attendance_records = {}


def mark_attendance(emp_id, date, status):
    """
    Record an attendance entry for an employee.

    status should be "Present" or "Absent".
    """
    record = {"date": date, "status": status}
    attendance_records.setdefault(emp_id, []).append(record)
    return record


def get_attendance(emp_id):
    """Return the list of attendance records for an employee."""
    return attendance_records.get(emp_id, [])


def calculate_attendance_percentage(emp_id):
    """Return the percentage of days marked 'Present' for an employee."""
    records = attendance_records.get(emp_id, [])
    if not records:
        return 0.0
    present_days = sum(1 for r in records if r["status"] == "Present")
    return round((present_days / len(records)) * 100, 2)

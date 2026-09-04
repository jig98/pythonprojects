"""
activity_log.py

Persists every terminal operation -- and its outcome -- to a single JSON
file on disk, so the session's activity (searches, rentals, returns,
registrations, invoices, history views, additions) has a permanent,
human-readable record that survives after the program exits.

The file is a JSON *array* of entry objects, growing by one entry per
operation, across every run of the program (it is never overwritten on
startup, only appended to). Each entry looks like:

{
  "timestamp": "2026-09-04T11:32:07",
  "action": "rent_vehicle",
  "status": "success",
  "details": { ... action-specific fields ... }
}

Using a plain JSON array (rather than JSON Lines) keeps the file directly
openable and readable in any JSON viewer, at the cost of a read-modify-
write on every entry -- an acceptable trade-off for a single-user console
app where operations happen at human typing speed, not high frequency.
"""

import json
import os
from datetime import date, datetime

DEFAULT_LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "activity_log.json",
)


def _json_safe(value):
    """Recursively convert dates/datetimes (and anything else json.dumps
    can't handle natively) into strings so log() never raises on ordinary
    domain objects like a rental's due_return_date."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


class ActivityLogger:
    def __init__(self, path: str = DEFAULT_LOG_PATH):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            self._write([])

    def log(self, action: str, status: str, details: dict) -> None:
        """Append one entry. status is typically 'success', 'blocked', or 'error'."""
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "action": action,
            "status": status,
            "details": _json_safe(details),
        }
        records = self._read()
        records.append(entry)
        self._write(records)

    def _read(self) -> list:
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write(self, records: list) -> None:
        with open(self.path, "w") as f:
            json.dump(records, f, indent=2)

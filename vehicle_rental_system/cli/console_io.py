"""
console_io.py

Small, reusable input helpers so every menu handler in cli/app.py gets
consistent validation and error messages instead of repeating try/except
blocks everywhere. Each function loops until the user provides valid input,
so the rest of the application can assume whatever it gets back is clean.
"""


def prompt_str(label: str, allow_empty: bool = False) -> str:
    while True:
        value = input(f"{label}: ").strip()
        if value or allow_empty:
            return value
        print("  This field can't be empty. Please try again.")


def prompt_int(label: str, min_value: int = None) -> int:
    while True:
        raw = input(f"{label}: ").strip()
        try:
            value = int(raw)
        except ValueError:
            print("  Please enter a whole number.")
            continue
        if min_value is not None and value < min_value:
            print(f"  Please enter a number of at least {min_value}.")
            continue
        return value


def prompt_float(label: str, min_value: float = None) -> float:
    while True:
        raw = input(f"{label}: ").strip()
        try:
            value = float(raw)
        except ValueError:
            print("  Please enter a number.")
            continue
        if min_value is not None and value < min_value:
            print(f"  Please enter a value of at least {min_value}.")
            continue
        return value


def prompt_choice(label: str, valid_choices) -> str:
    valid_choices = [str(c) for c in valid_choices]
    while True:
        value = input(f"{label} [{'/'.join(valid_choices)}]: ").strip()
        if value in valid_choices:
            return value
        print(f"  Invalid choice. Please enter one of: {', '.join(valid_choices)}")


def prompt_yes_no(label: str) -> bool:
    value = prompt_choice(f"{label} (y/n)", ["y", "n", "Y", "N"])
    return value.lower() == "y"


def pause():
    input("\nPress Enter to return to the menu...")

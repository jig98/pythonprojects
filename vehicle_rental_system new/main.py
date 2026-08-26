"""
main.py

Entry point. Run this file to start the interactive Vehicle Rental
Management System in your terminal:

    python main.py
"""

from cli import RentalApp


def main():
    app = RentalApp()
    app.run()


if __name__ == "__main__":
    main()

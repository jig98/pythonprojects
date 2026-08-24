

import logging

logging.basicConfig(
    filename="student_app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_student_name():
    """Ask for and validate the student's name (must not be empty)."""
    while True:
        name = input("Enter student name: ").strip()
        if name:
            logging.info(f"Student name received: {name}")
            return name
        print("Name cannot be empty. Please try again.")
        logging.warning("Empty student name entered.")


def get_number_of_subjects():
    """Ask for the number of subjects. Handles ValueError (Challenge 5 sets
    the stage for zero subjects, which is handled later in calculate_average)."""
    while True:
        try:
            num_subjects = int(input("Enter number of subjects: "))
        except ValueError:
            print("Please enter a valid number.")
            logging.error("Invalid input for number of subjects (ValueError).")
        else:
            if num_subjects < 0:
                print("Number of subjects cannot be negative.")
                logging.warning("Negative number of subjects entered.")
                continue
            logging.info(f"Number of subjects received: {num_subjects}")
            return num_subjects


def get_marks(num_subjects):
    """Collect marks for each subject. Handles ValueError and out-of-range marks."""
    marks = []
    for i in range(1, num_subjects + 1):
        while True:
            try:
                mark = float(input(f"Enter marks for subject {i}: "))
            except ValueError:
                print("Please enter a valid number.")
                logging.error(f"Invalid input for marks of subject {i} (ValueError).")
                continue
            else:
                if mark < 0 or mark > 100:
                    print("Marks must be between 0 and 100.")
                    print("Please enter the marks again.")
                    logging.warning(f"Out-of-range mark entered for subject {i}: {mark}")
                    continue
                if mark < 50:
                    logging.warning(f"Subject {i} mark is below passing range: {mark}")
                elif mark < 55:
                    logging.warning(
                        f"Subject {i} mark is close to the minimum passing mark: {mark}"
                    )
                marks.append(mark)
                break
    logging.info("Marks entered successfully.")
    return marks


# ---------------------------------------------------------------------------
# Core Logic (Challenge 2, 3 & 5)
# ---------------------------------------------------------------------------
def calculate_average(marks):
    """Accepts a list of marks, returns the average.
    Demonstrates try / except / else / finally, and handles ZeroDivisionError
    when the number of subjects is zero (Challenge 5)."""
    try:
        total = sum(marks)
        average = total / len(marks)
    except ZeroDivisionError:
        logging.error("ZeroDivisionError: cannot calculate average with zero subjects.")
        print("Cannot calculate average: no subjects were entered.")
        return None
    else:
        logging.debug(f"Average calculated successfully: {average:.2f}")
        return average
    finally:
        logging.debug("calculate_average() execution completed.")


def get_result(average):
    """Return the result category for a given average."""
    if average >= 90:
        return "Excellent"
    elif average >= 75:
        return "Very Good"
    elif average >= 50:
        return "Pass"
    else:
        return "Fail"


def display_statistics(marks, average, result):
    """Bonus Task: display highest, lowest, and average mark."""
    highest = max(marks)
    lowest = min(marks)
    print("\n----- Student Statistics ----")
    print(f"Highest Mark : {highest:.2f}")
    print(f"Lowest Mark  : {lowest:.2f}")
    print(f"Average Mark : {average:.2f}")
    print(f"Result       : {result}")
    logging.info("Student statistics calculated successfully.")


# ---------------------------------------------------------------------------
# Student Processing Flow
# ---------------------------------------------------------------------------
def process_student():
    """Runs the full flow for a single student, start to finish."""
    logging.info("Student processing started.")

    try:
        name = get_student_name()
        num_subjects = get_number_of_subjects()
        marks = get_marks(num_subjects)
        average = calculate_average(marks)
    except Exception as exc:
        
        logging.critical(f"Unexpected failure while processing student: {exc}")
        print("A serious error occurred and this student could not be processed.")
        return
    else:
        if average is None:
            logging.critical("Student processing could not be completed: zero subjects.")
            print("No subjects were entered, so no result could be calculated.")
        else:
            result = get_result(average)
            print("\n----- Student Result ----")
            print(f"Student Name : {name}")
            print(f"Average      : {average:.2f}")
            print(f"Result       : {result}")
            logging.info(f"Result determined for {name}: {result} (avg {average:.2f})")
            display_statistics(marks, average, result)
    finally:
        print("Processing completed.")
        logging.info("Student processing completed.")



def main():
    logging.info("Application started.")

    while True:
        process_student()

        again = input("\nDo you want to enter another student? (yes/no): ").strip().lower()
        if again != "yes":
            break

    logging.info("Application completed.")
    print("\nThank you for using the Student Result Processing System.")


if __name__ == "__main__":
    main()

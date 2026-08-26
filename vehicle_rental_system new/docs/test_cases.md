# Test Cases — Vehicle Rental Management System (Interactive CLI)

These are manual test cases you run against the live terminal menu in
`main.py`. Each one lists the exact menu path, the input to type, the
expected result, and the actual result observed. A full recorded session
covering the success-path cases is saved at
`docs/sample_terminal_session.txt` — open it alongside this table.

## How to test it yourself

```
python main.py
```
Then follow the menu prompts for each case below.

## Success paths

| # | Test case | Menu path & input | Expected result | Actual result |
|---|-----------|--------------------|------------------|----------------|
| 1 | View starting inventory | Option 1 | Shows the 3 preloaded vehicles (Car V101, Bike V102, Van V103) | Shown correctly — Pass |
| 2 | Register a customer | Option 3 → `C001`, `Ananya Sharma`, `ananya@example.com`, `DL-...` | "Customer registered successfully" with details echoed back | Confirmed — Pass |
| 3 | Rent a car | Option 4 → `C001` → `V101` → `3` days → Card payment | "Rental confirmed!" with Rental ID, base amount Rs. 6,000, due date, masked payment reference | Confirmed, `R0001`, Rs. 6,000.00 — Pass |
| 4 | Search by vehicle type | Option 2 → `2` → `Bike` | Returns only the Bike (V102) | 1 result, V102 — Pass |
| 5 | Search by price range | Option 2 → `3` → min `1000` → max `4000` | Returns Car and Van, not Bike | 2 results — Pass |
| 6 | Return a car on time | Option 5 → rental ID → `0` late days | Late fee Rs. 0, invoice final amount = base amount | 0 / matches base — Pass |
| 7 | Return a car 1 day late | Option 5 → rental ID → `1` late day (daily rate Rs. 2000) | Late fee = 1 x 20% x 2000 = Rs. 400; final = Rs. 6,400 | 400 / 6,400 — Pass |
| 8 | View invoice after return | Option 6 → rental ID | Full formatted invoice reprinted | Matches original — Pass |
| 9 | View rental history | Option 7 → customer ID | Lists the rental with status `RETURNED` and total amount | Shown correctly — Pass |
| 10 | Add a new vehicle | Option 8 → `V104` → `Bike` → reg. no. → brand → model → rate | "Vehicle added successfully", now appears in available list | Confirmed — Pass |
| 11 | Exit cleanly | Option 9 | Goodbye message, program ends, no traceback | Confirmed — Pass |

## Failure / validation paths

| # | Test case | Menu path & input | Expected result | Actual result |
|---|-----------|--------------------|------------------|----------------|
| 12 | Invalid menu choice | Type `99` at the main menu | Re-prompts with "Invalid choice..." instead of crashing | Re-prompted — Pass |
| 13 | Rent an already-rented vehicle | Rent `V101` to Customer A, then try renting `V101` again to Customer B | "Vehicle V101 (Car) is currently unavailable." — no payment step is even asked | Blocked before payment step — Pass |
| 14 | Rent with 0 or negative days | Option 4 → enter `0` for rental days | Re-prompts: "Please enter a number of at least 1." | Re-prompted — Pass |
| 15 | Rent an unknown vehicle ID | Option 4 → enter `V999` | "No vehicle found with ID V999." — returns to menu | Handled — Pass |
| 16 | Register a duplicate customer ID | Option 3 → reuse an existing customer ID | "A customer with ID ... already exists." | Blocked — Pass |
| 17 | Return an unknown rental ID | Option 5 → `R9999` | Caught `RentalNotFoundError`, printed as `[Error] ...`, no crash | Handled — Pass |
| 18 | View invoice before the vehicle is returned | Option 6 → a rental ID that's still active | "No invoice available for ... yet (vehicle may not be returned)." | Handled — Pass |
| 19 | Empty required field | Option 3 → leave name blank and press Enter | "This field can't be empty. Please try again." — re-prompts | Re-prompted — Pass |
| 20 | Non-numeric input where a number is expected | Option 4 → type `abc` for rental days | "Please enter a whole number." — re-prompts | Re-prompted — Pass |

**All cases above were run against the live CLI and passed.** See
`docs/sample_terminal_session.txt` for the recorded transcript of cases
1–3 and 6–10 run back-to-back in a single session.

# Assignment Answers: Python Exception Handling and Logging

## Logging Level Exercise

**Setup:** `logging.basicConfig(filename="student_app.log", level=logging.ERROR)`, then five
messages were logged, one at each level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

**Result with `level=logging.ERROR`** — only 2 of 5 lines were written:
```
ERROR - This is an ERROR message.
CRITICAL - This is a CRITICAL message.
```

| Log Level | Recorded? |
|-----------|-----------|
| DEBUG     | No        |
| INFO      | No        |
| WARNING   | No        |
| ERROR     | Yes       |
| CRITICAL  | Yes       |

**Result with `level=logging.DEBUG`** — all 5 of 5 lines were written:
```
DEBUG - This is a DEBUG message.
INFO - This is an INFO message.
WARNING - This is a WARNING message.
ERROR - This is an ERROR message.
CRITICAL - This is a CRITICAL message.
```

### 1. What difference do you observe?
At `ERROR` level, only the ERROR and CRITICAL lines appeared in the log file — the DEBUG,
INFO, and WARNING calls ran without raising any errors, but nothing was written for them.
At `DEBUG` level, every single message was written, in the order it was logged.

### 2. Why does changing the logging level affect the messages recorded in the log file?
Python's logging levels form a numeric hierarchy: `DEBUG (10) < INFO (20) < WARNING (30) <
ERROR (40) < CRITICAL (50)`. The `level` argument in `basicConfig()` sets a **threshold** —
the logger only writes messages whose level is *greater than or equal to* that threshold, and
silently drops (does not evaluate to disk) anything below it. Setting `level=logging.ERROR`
raises the bar so only ERROR and CRITICAL get through. Setting `level=logging.DEBUG` lowers
the bar all the way down, so everything gets through. The `logging.error(...)` /
`logging.info(...)` calls in the code don't change — what changes is which of those calls the
configured handler actually acts on.

---

## Conceptual Questions

**1. What is exception handling?**
Exception handling is a way of writing code that anticipates things that could go wrong at
runtime (bad input, division by zero, missing files, etc.) and responds to them in a
controlled way instead of letting the program crash. In Python this is done with `try`,
`except`, `else`, and `finally` blocks.

**2. Why should we use exception handling?**
Without it, any unexpected input or runtime condition crashes the whole program and can lose
whatever work was in progress, produce a raw, unfriendly traceback for the user, and leave
resources (files, connections) improperly closed. Exception handling lets the program recover,
show a clear message, and keep running.

**3. What is the difference between `try` and `except`?**
`try` wraps the code that *might* raise an exception — Python attempts to run it normally.
`except` defines what to do *if* a specific exception actually occurs while running the `try`
block. `try` is the attempt; `except` is the response to failure.

**4. When is the `else` block executed?**
The `else` block runs only if the code inside `try` completed **without** raising any
exception. It's useful for code that should run only on success, keeping it separate from the
risky code in `try`.

**5. When is the `finally` block executed?**
`finally` always runs, whether or not an exception occurred — even if the `except` block
handled it, even if the `try` succeeded via `else`, and even if an exception was raised and not
caught at all. It's typically used for cleanup that must happen no matter what (e.g., printing
"Processing completed.", closing a file).

**6. What is logging?**
Logging is the practice of recording events, state, and errors that occur while a program runs
to a persistent destination (in this case, a file) rather than just printing to the screen.
Python's `logging` module provides levels, timestamps, and configurable output so this record
is structured and useful after the fact.

**7. What is the difference between `print()` and logging?**
`print()` only shows text in the console at the moment it runs, has no severity levels, and is
usually stripped out before shipping code. `logging` writes persistently to a file (or other
destinations), supports severity levels (DEBUG through CRITICAL) so output can be filtered, and
includes context like timestamps automatically — making it suitable for diagnosing issues after
the program has already run, including in production.

**8. What happens when the logging level is set to ERROR? Which log levels will be recorded?**
Only messages logged at `ERROR` level or higher are recorded — that means `ERROR` and
`CRITICAL`. `DEBUG`, `INFO`, and `WARNING` calls are made in the code but produce no output in
the log file, as demonstrated above.

**9. What happens if we do not handle `ValueError` when converting user input using `int()`?**
If the user types something that isn't a valid integer (e.g., `"abc"`), `int("abc")` raises an
unhandled `ValueError`, and the program terminates immediately with a traceback shown to the
user. Any work already in progress for that run is lost, and the person running the program is
left with a confusing, technical error message instead of a helpful one.

**10. Why should we avoid using a broad exception handler such as `except: pass`?**
A bare `except: pass` silently swallows *every* exception — including ones that indicate real
bugs (typos, logic errors, `KeyboardInterrupt`) — and gives no indication anything went wrong.
This makes bugs extremely hard to find because the program appears to "work" while actually
failing silently. It's much better to catch specific exceptions you expect and know how to
handle, and to at least log anything unexpected.

**11. Why is logging useful in a production application?**
In production, developers usually can't watch the console output live or reproduce a user's
exact steps. A log file provides a persistent, timestamped history of what the application did
and what went wrong, which is essential for debugging issues after the fact, auditing behavior,
monitoring health, and spotting patterns (e.g., repeated errors) without needing to interrupt
the running system.

**12. What is the purpose of the `finally` block?**
`finally` guarantees that certain code — typically cleanup actions like closing files,
releasing resources, or printing a "done" message — runs regardless of whether the `try` block
succeeded, failed, or was handled by `except`. It ensures that essential wrap-up steps are never
skipped, even in error scenarios.

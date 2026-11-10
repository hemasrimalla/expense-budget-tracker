"""
Utility Module for Personal Expense & Budget Tracker.

Provides input validation, currency formatting, ASCII table rendering,
date parsing, and CLI formatting helpers.
"""

from datetime import datetime
import os
import re


# ---------------------------------------------------------------------------
# Formatting Helpers
# ---------------------------------------------------------------------------

def format_currency(amount: float) -> str:
    """
    Format a floating-point number into Indian Rupee (₹) currency format.

    Examples:
        >>> format_currency(1250.5)
        '₹1,250.50'
        >>> format_currency(-50.0)
        '-₹50.00'

    Args:
        amount: The numeric amount to format.

    Returns:
        Formatted currency string.
    """
    if amount < 0:
        return f"-₹{abs(amount):,.2f}"
    return f"₹{amount:,.2f}"


def create_progress_bar(percentage: float, width: int = 20) -> str:
    """
    Create an ASCII progress bar representing budget utilization.

    Args:
        percentage: Percentage utilized (e.g. 75.5 for 75.5%).
        width: Number of block characters in the bar.

    Returns:
        A string representing the visual bar and percentage,
        e.g., "[██████████░░░░░░░░░░] 50.0%".
    """
    clamped_pct = max(0.0, min(percentage, 100.0))
    filled_len = int(round(width * (clamped_pct / 100.0)))
    empty_len = width - filled_len
    bar = "█" * filled_len + "░" * empty_len
    return f"[{bar}] {percentage:.1f}%"


def print_table(headers: list[str], rows: list[list[str]], alignments: list[str] | None = None) -> None:
    """
    Print tabular data with clean ASCII border formatting.

    Args:
        headers: List of column header titles.
        rows: List of rows, where each row is a list of string values.
        alignments: Optional list specifying alignment for each column:
                    '<' for left, '>' for right, '^' for center.
                    Defaults to left-alignment for all columns.
    """
    if not headers:
        return

    num_cols = len(headers)
    if alignments is None:
        alignments = ["<"] * num_cols

    # Calculate maximum width required for each column
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for idx in range(min(num_cols, len(row))):
            col_widths[idx] = max(col_widths[idx], len(str(row[idx])))

    # Add 2 spaces of inner padding per column
    col_widths = [w + 2 for w in col_widths]

    # Create separator line
    sep_line = "+" + "+".join("-" * w for w in col_widths) + "+"

    # Format header row
    header_cells = []
    for idx, header in enumerate(headers):
        align = alignments[idx] if idx < len(alignments) else "<"
        cell = f" {header} "
        if align == ">":
            header_cells.append(cell.rjust(col_widths[idx]))
        elif align == "^":
            header_cells.append(cell.center(col_widths[idx]))
        else:
            header_cells.append(cell.ljust(col_widths[idx]))
    header_line = "|" + "|".join(header_cells) + "|"

    print(sep_line)
    print(header_line)
    print(sep_line)

    # Format each data row
    if not rows:
        empty_msg = " No records found ".center(sum(col_widths) + num_cols - 1)
        print(f"|{empty_msg}|")
        print(sep_line)
        return

    for row in rows:
        row_cells = []
        for idx in range(num_cols):
            val = str(row[idx]) if idx < len(row) else ""
            align = alignments[idx] if idx < len(alignments) else "<"
            cell = f" {val} "
            if align == ">":
                row_cells.append(cell.rjust(col_widths[idx]))
            elif align == "^":
                row_cells.append(cell.center(col_widths[idx]))
            else:
                row_cells.append(cell.ljust(col_widths[idx]))
        print("|" + "|".join(row_cells) + "|")

    print(sep_line)


# ---------------------------------------------------------------------------
# Input Validation Helpers
# ---------------------------------------------------------------------------

def get_valid_amount(
    prompt: str,
    allow_zero: bool = False,
    default: float | None = None
) -> float:
    """
    Prompt user for a valid positive monetary amount with exception handling.

    Args:
        prompt: Display message for the input prompt.
        allow_zero: If True, 0.0 is considered valid.
        default: Optional default value used if user presses Enter without input.

    Returns:
        A valid positive float.
    """
    while True:
        suffix = f" [default: {format_currency(default)}]: " if default is not None else ": "
        user_input = input(prompt + suffix).strip().replace(",", "")

        if not user_input and default is not None:
            return float(default)

        if not user_input:
            print("  [!] Error: Amount cannot be empty. Please enter a valid number.")
            continue

        try:
            val = float(user_input)
            if val < 0:
                print("  [!] Error: Amount cannot be negative. Please enter a positive value.")
                continue
            if val == 0 and not allow_zero:
                print("  [!] Error: Amount must be greater than zero.")
                continue
            return round(val, 2)
        except ValueError:
            print("  [!] Error: Invalid numeric value. Please enter a valid amount (e.g. 250 or 1500.50).")


def get_valid_date(
    prompt: str = "Enter date (YYYY-MM-DD)",
    default_today: bool = True,
    default_val: str | None = None
) -> str:
    """
    Prompt user for a valid calendar date in YYYY-MM-DD format.

    Args:
        prompt: The input prompt message.
        default_today: If True and default_val is None, defaults to current date.
        default_val: Specific default date string to use on empty input.

    Returns:
        Validated date string in 'YYYY-MM-DD' format.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    effective_default = default_val if default_val is not None else (today_str if default_today else None)

    while True:
        suffix = f" [default: {effective_default}]: " if effective_default else ": "
        user_input = input(prompt + suffix).strip()

        if not user_input and effective_default:
            return effective_default

        if not user_input:
            print("  [!] Error: Date cannot be empty. Expected format: YYYY-MM-DD.")
            continue

        try:
            parsed = datetime.strptime(user_input, "%Y-%m-%d")
            # Extra safety check against unreasonable years
            if parsed.year < 1900 or parsed.year > 2100:
                print("  [!] Error: Year must be between 1900 and 2100.")
                continue
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            print("  [!] Error: Invalid date format or non-existent date. Use YYYY-MM-DD (e.g., 2026-11-10).")


def get_valid_month(
    prompt: str = "Enter month (YYYY-MM)",
    default_current: bool = True,
    default_val: str | None = None
) -> str:
    """
    Prompt user for a valid month in YYYY-MM format.

    Args:
        prompt: The input prompt message.
        default_current: If True and default_val is None, defaults to current month.
        default_val: Specific default month string on empty input.

    Returns:
        Validated month string in 'YYYY-MM' format.
    """
    current_month = datetime.now().strftime("%Y-%m")
    effective_default = default_val if default_val is not None else (current_month if default_current else None)

    while True:
        suffix = f" [default: {effective_default}]: " if effective_default else ": "
        user_input = input(prompt + suffix).strip()

        if not user_input and effective_default:
            return effective_default

        if not user_input:
            print("  [!] Error: Month cannot be empty. Expected format: YYYY-MM.")
            continue

        try:
            parsed = datetime.strptime(user_input, "%Y-%m")
            if parsed.year < 1900 or parsed.year > 2100:
                print("  [!] Error: Year must be between 1900 and 2100.")
                continue
            return parsed.strftime("%Y-%m")
        except ValueError:
            print("  [!] Error: Invalid month format. Please use YYYY-MM (e.g., 2026-11).")


def get_valid_string(
    prompt: str,
    allow_empty: bool = False,
    default_val: str | None = None
) -> str:
    """
    Prompt user for a non-empty string or accept a default value.

    Args:
        prompt: Display message.
        allow_empty: Whether an empty string is permissible.
        default_val: Value returned when user hits Enter without typing.

    Returns:
        Cleaned string value.
    """
    while True:
        suffix = f" [default: {default_val}]: " if default_val is not None else ": "
        user_input = input(prompt + suffix).strip()

        if not user_input and default_val is not None:
            return default_val

        if not user_input and not allow_empty:
            print("  [!] Error: Input cannot be empty. Please enter a value.")
            continue

        return user_input


def get_valid_choice(prompt: str, valid_choices: list[str] | set[str]) -> str:
    """
    Prompt user until they enter one of the valid choice keys.

    Args:
        prompt: Input message.
        valid_choices: Collection of allowed option strings.

    Returns:
        The matched choice string.
    """
    valid_set = {str(c).strip().lower() for c in valid_choices}
    while True:
        choice = input(prompt).strip().lower()
        if choice in valid_set:
            return choice
        print(f"  [!] Invalid choice. Please choose from: {', '.join(sorted(valid_choices))}")


def get_confirmation(prompt: str = "Are you sure? (y/n)", default_no: bool = True) -> bool:
    """
    Prompt user for yes/no confirmation.

    Args:
        prompt: Confirmation prompt string.
        default_no: If True, hitting Enter defaults to No.

    Returns:
        True if confirmed (y/yes), False otherwise.
    """
    suffix = " [y/N]: " if default_no else " [Y/n]: "
    choice = input(prompt + suffix).strip().lower()
    if not choice:
        return not default_no
    return choice in ("y", "yes")


def clear_screen() -> None:
    """Clear terminal screen in a cross-platform manner."""
    os.system("cls" if os.name == "nt" else "clear")


def pause_for_user(prompt: str = "\nPress Enter to return to menu...") -> None:
    """Pause execution until the user presses Enter."""
    try:
        input(prompt)
    except (KeyboardInterrupt, EOFError):
        pass

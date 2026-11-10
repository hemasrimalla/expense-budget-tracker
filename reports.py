"""
Reports and Analytics Module for Personal Expense & Budget Tracker.

Calculates spending summaries, category breakdowns with percentage contributions,
identifies highest spending categories, calculates average daily spend,
and performs month-over-month comparisons with ASCII visualizations.
"""

import calendar
from datetime import datetime
from typing import Any

from utils import (
    format_currency,
    get_valid_choice,
    get_valid_month,
    print_table,
)


def get_days_in_month(year: int, month: int) -> int:
    """Return the total number of days in a given year and month."""
    return calendar.monthrange(year, month)[1]


def render_ascii_bar(ratio: float, max_width: int = 24) -> str:
    """
    Render a horizontal ASCII bar representing relative proportion.

    Args:
        ratio: Value between 0.0 and 1.0.
        max_width: Maximum length of the bar in characters.

    Returns:
        String of filled bar characters.
    """
    clamped = max(0.0, min(ratio, 1.0))
    length = int(round(clamped * max_width))
    return "█" * length + "░" * (max_width - length)


def generate_monthly_summary(
    expenses: list[dict[str, Any]],
    month_key: str | None = None
) -> None:
    """
    Generate and print a detailed spending summary for a specific month.

    Includes:
    - Total monthly spend
    - Total transaction count
    - Category-wise totals and percentages of total monthly spending
    - Highest and lowest spending categories
    - Highest single expense
    - Average daily spend (based on elapsed or full days)
    - ASCII visual distribution chart

    Args:
        expenses: Full list of expenses.
        month_key: Target month 'YYYY-MM'. If None, prompts the user.
    """
    if month_key is None:
        month_key = get_valid_month("Enter month for summary (YYYY-MM)", default_current=True)

    month_expenses = [exp for exp in expenses if exp.get("date", "").startswith(month_key)]

    print("\n" + "=" * 65)
    print(f"        MONTHLY SPENDING REPORT: {month_key}".center(65))
    print("=" * 65)

    if not month_expenses:
        print(f"\n  No expenses recorded for {month_key}.\n")
        return

    total_spent = sum(float(exp.get("amount", 0.0)) for exp in month_expenses)
    count = len(month_expenses)

    # Category totals
    cat_totals: dict[str, float] = {}
    cat_counts: dict[str, int] = {}
    for exp in month_expenses:
        cat = exp.get("category", "Other")
        amt = float(exp.get("amount", 0.0))
        cat_totals[cat] = cat_totals.get(cat, 0.0) + amt
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    # Sorted categories by spending
    sorted_cats = sorted(cat_totals.items(), key=lambda item: item[1], reverse=True)
    top_cat, top_cat_amt = sorted_cats[0]
    lowest_cat, lowest_cat_amt = sorted_cats[-1]

    # Highest single expense
    max_expense = max(month_expenses, key=lambda exp: float(exp.get("amount", 0.0)))

    # Daily average calculation
    year, month = map(int, month_key.split("-"))
    total_days = get_days_in_month(year, month)
    today = datetime.now()

    # If report is for current month and year, compute daily average based on days passed
    if year == today.year and month == today.month:
        effective_days = max(1, today.day)
        daily_avg = total_spent / effective_days
        days_note = f"(based on {effective_days} days elapsed in current month)"
    else:
        daily_avg = total_spent / total_days
        days_note = f"(based on {total_days} days in month)"

    # Print high-level metrics
    print(f"\n  • Total Amount Spent    : {format_currency(total_spent)}")
    print(f"  • Total Transactions    : {count}")
    print(f"  • Average per Expense   : {format_currency(total_spent / count)}")
    print(f"  • Average Daily Spend   : {format_currency(daily_avg)} {days_note}")
    print(f"  • Top Spending Category : {top_cat} ({format_currency(top_cat_amt)} - {(top_cat_amt / total_spent * 100):.1f}%)")
    print(f"  • Lowest Category       : {lowest_cat} ({format_currency(lowest_cat_amt)})")
    print(f"  • Largest Single Expense: {format_currency(max_expense['amount'])} ({max_expense['description']} on {max_expense['date']})")

    # Category breakdown table
    print("\n--- Category Breakdown ---")
    headers = ["Category", "Total Spent", "% of Month", "Count", "Distribution"]
    rows = []

    for cat, amt in sorted_cats:
        pct = (amt / total_spent * 100.0) if total_spent > 0 else 0.0
        bar = render_ascii_bar(amt / total_spent if total_spent > 0 else 0.0, max_width=15)
        rows.append([
            cat,
            format_currency(amt),
            f"{pct:.1f}%",
            str(cat_counts.get(cat, 0)),
            bar,
        ])

    print_table(headers, rows, alignments=["<", ">", ">", "^", "<"])
    print()


def generate_monthly_comparison(expenses: list[dict[str, Any]]) -> None:
    """
    Compare spending across all recorded months chronologically.

    Calculates:
    - Monthly total spend
    - Transaction count
    - Top spending category per month
    - Month-over-month % increase or decrease
    """
    print("\n" + "=" * 65)
    print("            MONTH-OVER-MONTH SPENDING COMPARISON".center(65))
    print("=" * 65)

    if not expenses:
        print("\n  No expense records available to compare.\n")
        return

    # Group expenses by month
    month_data: dict[str, list[dict[str, Any]]] = {}
    for exp in expenses:
        m = exp.get("date", "")[:7]
        if m:
            month_data.setdefault(m, []).append(exp)

    sorted_months = sorted(month_data.keys())
    if not sorted_months:
        print("\n  No valid month records found.\n")
        return

    headers = ["Month", "Total Spent", "Transactions", "Top Category", "MoM Change"]
    rows = []
    prev_spend: float | None = None

    for m in sorted_months:
        m_expenses = month_data[m]
        m_total = sum(float(exp.get("amount", 0.0)) for exp in m_expenses)
        count = len(m_expenses)

        # Top category in that month
        cat_map: dict[str, float] = {}
        for exp in m_expenses:
            cat = exp.get("category", "Other")
            cat_map[cat] = cat_map.get(cat, 0.0) + float(exp.get("amount", 0.0))
        top_cat = max(cat_map.items(), key=lambda x: x[1])[0] if cat_map else "None"

        # Month-over-month calculation
        if prev_spend is None or prev_spend == 0:
            mom_str = "Baseline"
        else:
            diff = m_total - prev_spend
            pct_change = (diff / prev_spend) * 100.0
            sign = "+" if pct_change > 0 else ""
            mom_str = f"{sign}{pct_change:.1f}%"

        rows.append([
            m,
            format_currency(m_total),
            str(count),
            top_cat,
            mom_str,
        ])
        prev_spend = m_total

    print()
    print_table(headers, rows, alignments=["^", ">", "^", "<", ">"])
    print()


def generate_all_time_category_summary(expenses: list[dict[str, Any]]) -> None:
    """Display all-time category spending summary and share."""
    print("\n" + "=" * 65)
    print("              ALL-TIME CATEGORY SPENDING".center(65))
    print("=" * 65)

    if not expenses:
        print("\n  No expense records available.\n")
        return

    total_all = sum(float(exp.get("amount", 0.0)) for exp in expenses)
    cat_map: dict[str, float] = {}
    cat_counts: dict[str, int] = {}

    for exp in expenses:
        cat = exp.get("category", "Other")
        amt = float(exp.get("amount", 0.0))
        cat_map[cat] = cat_map.get(cat, 0.0) + amt
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    sorted_cats = sorted(cat_map.items(), key=lambda x: x[1], reverse=True)

    headers = ["Category", "All-Time Spend", "% Share", "Transactions", "Visual Share"]
    rows = []

    for cat, amt in sorted_cats:
        pct = (amt / total_all * 100.0) if total_all > 0 else 0.0
        bar = render_ascii_bar(amt / total_all if total_all > 0 else 0.0, max_width=15)
        rows.append([
            cat,
            format_currency(amt),
            f"{pct:.1f}%",
            str(cat_counts.get(cat, 0)),
            bar,
        ])

    print()
    print_table(headers, rows, alignments=["<", ">", ">", "^", "<"])
    print(f" Total All-Time Expenses: {len(expenses)} | Total Spent: {format_currency(total_all)}\n")


def reports_menu_flow(expenses: list[dict[str, Any]]) -> None:
    """Submenu for spending reports and analytics."""
    while True:
        print("\n" + "=" * 50)
        print("            SPENDING REPORTS & ANALYTICS")
        print("=" * 50)
        print("  [1] Monthly Spending Summary (Metrics & Chart)")
        print("  [2] Month-over-Month Comparison")
        print("  [3] All-Time Category Breakdown")
        print("  [0] Return to Main Menu")
        print("=" * 50)

        choice = get_valid_choice("Enter choice [0-3]: ", ["0", "1", "2", "3"])

        if choice == "0":
            break
        elif choice == "1":
            generate_monthly_summary(expenses)
        elif choice == "2":
            generate_monthly_comparison(expenses)
        elif choice == "3":
            generate_all_time_category_summary(expenses)

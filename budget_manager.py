"""
Budget Manager Module for Personal Expense & Budget Tracker.

Handles setting and tracking monthly budgets (overall and category-specific),
calculating remaining balances and utilization percentages, displaying visual
progress bars, and warning when spending reaches 80% or exceeds 100%.
"""

from typing import Any

from expense_manager import get_all_categories
from storage import save_budgets
from utils import (
    create_progress_bar,
    format_currency,
    get_confirmation,
    get_valid_amount,
    get_valid_choice,
    get_valid_month,
    print_table,
)


def get_month_spending(
    expenses: list[dict[str, Any]],
    month_key: str
) -> tuple[float, dict[str, float]]:
    """
    Calculate total and category-wise spending for a given month (YYYY-MM).

    Args:
        expenses: Full list of expense dictionaries.
        month_key: Target month string (e.g. '2026-11').

    Returns:
        A tuple of (total_month_spent, category_spending_dict).
    """
    total_spent = 0.0
    category_spending: dict[str, float] = {}

    for exp in expenses:
        exp_date = exp.get("date", "")
        if exp_date.startswith(month_key):
            amt = float(exp.get("amount", 0.0))
            cat = exp.get("category", "Other")
            total_spent += amt
            category_spending[cat] = category_spending.get(cat, 0.0) + amt

    return total_spent, category_spending


def view_monthly_budget_status(
    budgets: dict[str, Any],
    expenses: list[dict[str, Any]],
    month_key: str | None = None
) -> None:
    """
    Display comprehensive budget status for a given month.

    Includes total budget status, visual progress bar, warning status,
    and category-specific breakdowns.

    Args:
        budgets: Budget dictionary.
        expenses: Expense list.
        month_key: Target month (YYYY-MM). If None, prompts the user.
    """
    if month_key is None:
        month_key = get_valid_month("Enter month to check budget (YYYY-MM)", default_current=True)

    month_data = budgets.get(month_key, {})
    total_budget = float(month_data.get("total_budget", 0.0))
    cat_budgets: dict[str, float] = {
        k: float(v) for k, v in month_data.get("category_budgets", {}).items()
    }

    total_spent, cat_spending = get_month_spending(expenses, month_key)

    print("\n" + "=" * 65)
    print(f"       BUDGET STATUS FOR {month_key}".center(65))
    print("=" * 65)

    if total_budget <= 0 and not cat_budgets:
        print(f"\n  [i] No budget configured for {month_key}.")
        print(f"  Total Spending recorded in {month_key}: {format_currency(total_spent)}")
        if cat_spending:
            print("  Category Spending:")
            for cat, amt in sorted(cat_spending.items(), key=lambda x: x[1], reverse=True):
                print(f"    - {cat}: {format_currency(amt)}")
        print("\n  Tip: Use option [2] to set a total budget for this month.\n")
        return

    # 1. Total Monthly Budget Summary
    remaining = total_budget - total_spent
    pct_used = (total_spent / total_budget * 100.0) if total_budget > 0 else 0.0

    print(f"\nTotal Budget : {format_currency(total_budget)}")
    print(f"Total Spent  : {format_currency(total_spent)}")
    print(f"Remaining    : {format_currency(remaining)}")
    print(f"Utilization  : {create_progress_bar(pct_used)}")

    # Warning / Exceeded status badge
    if total_budget > 0:
        if pct_used > 100.0:
            over = total_spent - total_budget
            print(f"Status       : [!] EXCEEDED by {format_currency(over)} ({(pct_used - 100):.1f}% over budget)")
        elif pct_used >= 80.0:
            print(f"Status       : [!] WARNING: 80%+ Utilized ({pct_used:.1f}% of budget consumed)")
        else:
            print(f"Status       : [OK] On Track ({(100 - pct_used):.1f}% remaining)")

    # 2. Category Budgets Table
    all_cats = sorted(set(list(cat_budgets.keys()) + list(cat_spending.keys())))
    if all_cats:
        print("\nCategory-wise Budget Breakdown:")
        cat_headers = ["Category", "Budget", "Spent", "Remaining", "Used %", "Status"]
        cat_rows = []

        for cat in all_cats:
            c_budget = cat_budgets.get(cat, 0.0)
            c_spent = cat_spending.get(cat, 0.0)
            c_rem = c_budget - c_spent if c_budget > 0 else -c_spent

            if c_budget > 0:
                c_pct = (c_spent / c_budget) * 100.0
                c_pct_str = f"{c_pct:.1f}%"
                if c_pct > 100.0:
                    status = "EXCEEDED"
                elif c_pct >= 80.0:
                    status = "WARNING"
                else:
                    status = "OK"
                budget_str = format_currency(c_budget)
                rem_str = format_currency(c_rem)
            else:
                budget_str = "No Budget"
                c_pct_str = "-"
                status = "Untracked"
                rem_str = "-"

            cat_rows.append([
                cat,
                budget_str,
                format_currency(c_spent),
                rem_str,
                c_pct_str,
                status,
            ])

        print_table(
            cat_headers,
            cat_rows,
            alignments=["<", ">", ">", ">", ">", "^"]
        )
    print()


def set_monthly_budget(budgets: dict[str, Any]) -> dict[str, Any]:
    """
    Set or update the overall budget for a month.

    Args:
        budgets: Budget dictionary.

    Returns:
        Updated budgets dictionary.
    """
    print("\n" + "=" * 50)
    print("           SET MONTHLY OVERALL BUDGET")
    print("=" * 50)

    month_key = get_valid_month("Enter month (YYYY-MM)", default_current=True)
    current_data = budgets.get(month_key, {})
    current_total = current_data.get("total_budget", 0.0)

    if current_total > 0:
        print(f"Current overall budget for {month_key}: {format_currency(current_total)}")

    amount = get_valid_amount("Enter overall budget amount for the month (₹)")

    if month_key not in budgets:
        budgets[month_key] = {"total_budget": amount, "category_budgets": {}}
    else:
        budgets[month_key]["total_budget"] = amount

    if save_budgets(budgets):
        print(f"\n[OK] Monthly budget of {format_currency(amount)} saved for {month_key}!")
    else:
        print("\n[!] Failed to save budget to storage.")

    return budgets


def set_category_budget(
    budgets: dict[str, Any],
    expenses: list[dict[str, Any]],
    custom_categories: set[str] | None = None
) -> dict[str, Any]:
    """
    Set or update a budget for a specific category within a month.

    Args:
        budgets: Budget dictionary.
        expenses: Expense list to source available categories.
        custom_categories: Custom categories set.

    Returns:
        Updated budgets dictionary.
    """
    print("\n" + "=" * 50)
    print("           SET CATEGORY-WISE BUDGET")
    print("=" * 50)

    month_key = get_valid_month("Enter month (YYYY-MM)", default_current=True)
    if month_key not in budgets:
        budgets[month_key] = {"total_budget": 0.0, "category_budgets": {}}
    elif "category_budgets" not in budgets[month_key]:
        budgets[month_key]["category_budgets"] = {}

    cats = get_all_categories(expenses, custom_categories)
    print(f"\nAvailable Categories for {month_key}:")
    for idx, c in enumerate(cats, start=1):
        curr_b = budgets[month_key]["category_budgets"].get(c, 0.0)
        curr_str = f" [Current: {format_currency(curr_b)}]" if curr_b > 0 else ""
        print(f"  [{idx}] {c}{curr_str}")

    cat_idx = int(get_valid_choice("Select category number: ", [str(i) for i in range(1, len(cats) + 1)]))
    chosen_cat = cats[cat_idx - 1]

    print(f"\nSetting budget for category: '{chosen_cat}' in month {month_key}")
    amount = get_valid_amount("Enter budget amount (₹, enter 0 to remove budget)", allow_zero=True)

    if amount == 0:
        if chosen_cat in budgets[month_key]["category_budgets"]:
            del budgets[month_key]["category_budgets"][chosen_cat]
            print(f"[OK] Budget for '{chosen_cat}' removed.")
    else:
        budgets[month_key]["category_budgets"][chosen_cat] = amount
        print(f"[OK] Budget for '{chosen_cat}' set to {format_currency(amount)} for {month_key}!")

    save_budgets(budgets)
    return budgets


def list_all_budgets(budgets: dict[str, Any]) -> None:
    """Display an overview table of all months with configured budgets."""
    print("\n" + "=" * 65)
    print("              ALL CONFIGURED BUDGETS".center(65))
    print("=" * 65)

    if not budgets:
        print("\n  No budgets configured yet.\n")
        return

    headers = ["Month", "Overall Budget", "Category Budgets Defined"]
    rows = []

    for month_key in sorted(budgets.keys(), reverse=True):
        m_info = budgets[month_key]
        total_b = m_info.get("total_budget", 0.0)
        cat_count = len(m_info.get("category_budgets", {}))
        rows.append([
            month_key,
            format_currency(total_b) if total_b > 0 else "Not set",
            f"{cat_count} categories" if cat_count > 0 else "None",
        ])

    print_table(headers, rows, alignments=["^", ">", "^"])
    print()


def budget_menu_flow(
    budgets: dict[str, Any],
    expenses: list[dict[str, Any]],
    custom_categories: set[str] | None = None
) -> dict[str, Any]:
    """Submenu for budget management."""
    while True:
        print("\n" + "=" * 50)
        print("                 BUDGET MANAGER")
        print("=" * 50)
        print("  [1] Check Monthly Budget Status & Warnings")
        print("  [2] Set / Update Total Monthly Budget")
        print("  [3] Set / Update Category-Specific Budget")
        print("  [4] View All Configured Budgets")
        print("  [5] Delete a Month's Budget")
        print("  [0] Return to Main Menu")
        print("=" * 50)

        choice = get_valid_choice("Enter choice [0-5]: ", ["0", "1", "2", "3", "4", "5"])

        if choice == "0":
            break
        elif choice == "1":
            view_monthly_budget_status(budgets, expenses)
        elif choice == "2":
            budgets = set_monthly_budget(budgets)
        elif choice == "3":
            budgets = set_category_budget(budgets, expenses, custom_categories)
        elif choice == "4":
            list_all_budgets(budgets)
        elif choice == "5":
            month_key = get_valid_month("Enter month to delete budget for (YYYY-MM)")
            if month_key in budgets:
                confirm = get_confirmation(f"Delete budget for {month_key}?", default_no=True)
                if confirm:
                    del budgets[month_key]
                    save_budgets(budgets)
                    print(f"[OK] Budget for {month_key} deleted.")
            else:
                print(f"[!] No budget found for {month_key}.")

    return budgets

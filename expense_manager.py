"""
Expense Manager Module for Personal Expense & Budget Tracker.

Handles adding, viewing, editing, deleting, searching, filtering, and sorting expenses.
Supports predefined and custom categories with input validation and instant budget alerts.
"""

from datetime import datetime
from typing import Any

from storage import save_expenses
from utils import (
    create_progress_bar,
    format_currency,
    get_confirmation,
    get_valid_amount,
    get_valid_choice,
    get_valid_date,
    get_valid_month,
    get_valid_string,
    print_table,
)

# Standard predefined expense categories
DEFAULT_CATEGORIES = [
    "Food",
    "Transport",
    "Rent",
    "Bills",
    "Shopping",
    "Health",
    "Entertainment",
    "Other",
]


def get_all_categories(expenses: list[dict[str, Any]], custom_categories: set[str] | None = None) -> list[str]:
    """
    Get a complete sorted list of all unique categories.

    Combines standard default categories with custom categories and any
    already present in existing expense records.

    Args:
        expenses: Current list of expenses.
        custom_categories: Optional set of user-added custom categories.

    Returns:
        Sorted list of distinct category names.
    """
    cats = set(DEFAULT_CATEGORIES)
    if custom_categories:
        cats.update(custom_categories)
    for exp in expenses:
        cat = exp.get("category")
        if cat:
            cats.add(cat.strip().title())
    return sorted(cats)


def choose_or_add_category(categories: list[str]) -> str:
    """
    Display available categories and prompt user to select one or add a new custom category.

    Args:
        categories: List of currently available categories.

    Returns:
        The selected or newly created category name.
    """
    print("\n--- Select Category ---")
    for idx, cat in enumerate(categories, start=1):
        print(f"  [{idx}] {cat}")
    print(f"  [{len(categories) + 1}] + Add New Custom Category")

    valid_choices = [str(i) for i in range(1, len(categories) + 2)]
    choice = int(get_valid_choice("Enter choice: ", valid_choices))

    if choice <= len(categories):
        return categories[choice - 1]
    else:
        # Prompt for custom category name
        while True:
            new_cat = get_valid_string("Enter new category name: ").strip().title()
            if not new_cat:
                print("  [!] Category name cannot be empty.")
                continue
            return new_cat


def get_next_expense_id(expenses: list[dict[str, Any]]) -> int:
    """Compute the next available unique integer ID for an expense."""
    if not expenses:
        return 1
    return max(exp.get("id", 0) for exp in expenses) + 1


def add_expense_flow(
    expenses: list[dict[str, Any]],
    budgets: dict[str, Any],
    custom_categories: set[str] | None = None
) -> list[dict[str, Any]]:
    """
    Interactive prompt to add a new expense.

    Validates fields, saves to JSON storage, and checks against monthly budget
    to alert the user if spending exceeds 80% or 100%.

    Args:
        expenses: Mutable list of expenses.
        budgets: Budget dictionary for alert checking.
        custom_categories: Optional set of custom categories.

    Returns:
        Updated list of expenses.
    """
    print("\n" + "=" * 50)
    print("               ADD NEW EXPENSE")
    print("=" * 50)

    # 1. Date
    date_val = get_valid_date("Enter expense date (YYYY-MM-DD)", default_today=True)

    # 2. Amount
    amount = get_valid_amount("Enter expense amount (₹)")

    # 3. Category
    available_cats = get_all_categories(expenses, custom_categories)
    category = choose_or_add_category(available_cats)
    if custom_categories is not None and category not in DEFAULT_CATEGORIES:
        custom_categories.add(category)

    # 4. Description
    description = get_valid_string("Enter description / note", allow_empty=False)

    # Generate ID and create new record
    new_id = get_next_expense_id(expenses)
    new_expense = {
        "id": new_id,
        "date": date_val,
        "amount": amount,
        "category": category,
        "description": description,
    }

    expenses.append(new_expense)

    if save_expenses(expenses):
        print(f"\n[OK] Expense ID #{new_id} added successfully!")
        print_table(
            headers=["ID", "Date", "Amount", "Category", "Description"],
            rows=[[str(new_id), date_val, format_currency(amount), category, description]],
            alignments=["^", "^", ">", "<", "<"],
        )

        # Check for budget warnings for this month
        month_key = date_val[:7]
        _check_and_print_budget_alert(expenses, budgets, month_key, category)
    else:
        print("\n[!] Failed to save expense to storage.")

    return expenses


def _check_and_print_budget_alert(
    expenses: list[dict[str, Any]],
    budgets: dict[str, Any],
    month_key: str,
    category: str
) -> None:
    """Internal helper to check and display immediate budget alert after adding an expense."""
    month_budget_info = budgets.get(month_key)
    if not month_budget_info:
        return

    # Check overall month budget
    total_budget = month_budget_info.get("total_budget", 0.0)
    if total_budget > 0:
        total_spent = sum(
            exp.get("amount", 0.0)
            for exp in expenses
            if exp.get("date", "").startswith(month_key)
        )
        pct = (total_spent / total_budget) * 100.0
        if pct >= 100.0:
            over = total_spent - total_budget
            print(f"\n>>> [BUDGET ALERT] Overall budget for {month_key} EXCEEDED!")
            print(f"    Spent: {format_currency(total_spent)} / Budget: {format_currency(total_budget)} ({pct:.1f}%)")
            print(f"    Over budget by: {format_currency(over)}")
        elif pct >= 80.0:
            remaining = total_budget - total_spent
            print(f"\n>>> [BUDGET WARNING] Overall budget for {month_key} reached {pct:.1f}%!")
            print(f"    Spent: {format_currency(total_spent)} / Budget: {format_currency(total_budget)}")
            print(f"    Remaining budget: {format_currency(remaining)}")

    # Check category budget if defined
    cat_budgets = month_budget_info.get("category_budgets", {})
    if category in cat_budgets and cat_budgets[category] > 0:
        cat_budget = cat_budgets[category]
        cat_spent = sum(
            exp.get("amount", 0.0)
            for exp in expenses
            if exp.get("date", "").startswith(month_key) and exp.get("category") == category
        )
        cat_pct = (cat_spent / cat_budget) * 100.0
        if cat_pct >= 100.0:
            print(f">>> [CATEGORY ALERT] Budget for '{category}' in {month_key} EXCEEDED ({cat_pct:.1f}%)!")
        elif cat_pct >= 80.0:
            print(f">>> [CATEGORY WARNING] Budget for '{category}' in {month_key} reached {cat_pct:.1f}%!")


def view_expenses_table(expenses: list[dict[str, Any]], title: str = "All Expenses") -> None:
    """
    Display a formatted ASCII table of expenses with count and total spend.

    Args:
        expenses: List of expense dictionaries.
        title: Header banner title.
    """
    print("\n" + "=" * 65)
    print(title.center(65))
    print("=" * 65)

    if not expenses:
        print("\n  No expense records found.\n")
        return

    headers = ["ID", "Date", "Amount", "Category", "Description"]
    rows = []
    total_amount = 0.0

    for exp in expenses:
        amt = exp.get("amount", 0.0)
        total_amount += amt
        rows.append([
            str(exp.get("id", "")),
            exp.get("date", ""),
            format_currency(amt),
            exp.get("category", ""),
            exp.get("description", ""),
        ])

    print_table(headers, rows, alignments=["^", "^", ">", "<", "<"])
    print(f" Total Expenses: {len(expenses)} | Total Spent: {format_currency(total_amount)}\n")


def edit_expense_flow(
    expenses: list[dict[str, Any]],
    custom_categories: set[str] | None = None
) -> list[dict[str, Any]]:
    """
    Prompt user to edit an existing expense record by ID.

    Allows user to press Enter to keep current values for each field.

    Args:
        expenses: List of expense dictionaries.
        custom_categories: Optional set of custom categories.

    Returns:
        Updated list of expenses.
    """
    print("\n" + "=" * 50)
    print("                EDIT EXPENSE")
    print("=" * 50)

    if not expenses:
        print("  No expenses available to edit.")
        return expenses

    while True:
        id_input = input("Enter Expense ID to edit (or 'c' to cancel): ").strip()
        if id_input.lower() == "c":
            return expenses

        try:
            target_id = int(id_input)
            break
        except ValueError:
            print("  [!] Please enter a valid numerical ID.")

    # Find the target expense
    target_exp = next((exp for exp in expenses if exp.get("id") == target_id), None)
    if not target_exp:
        print(f"  [!] Expense with ID #{target_id} not found.")
        return expenses

    print("\nCurrent Expense Details:")
    print_table(
        headers=["ID", "Date", "Amount", "Category", "Description"],
        rows=[[
            str(target_exp.get("id")),
            target_exp.get("date", ""),
            format_currency(target_exp.get("amount", 0.0)),
            target_exp.get("category", ""),
            target_exp.get("description", ""),
        ]],
        alignments=["^", "^", ">", "<", "<"],
    )
    print("Press Enter to keep current value, or type new value:\n")

    # 1. Date
    new_date = get_valid_date(
        "Enter new date (YYYY-MM-DD)",
        default_val=target_exp.get("date")
    )

    # 2. Amount
    new_amount = get_valid_amount(
        "Enter new amount (₹)",
        default=target_exp.get("amount")
    )

    # 3. Category
    current_cat = target_exp.get("category", "Other")
    print(f"\nCurrent category is: '{current_cat}'")
    change_cat = get_confirmation("Do you want to change the category?", default_no=True)
    if change_cat:
        available_cats = get_all_categories(expenses, custom_categories)
        new_category = choose_or_add_category(available_cats)
        if custom_categories is not None and new_category not in DEFAULT_CATEGORIES:
            custom_categories.add(new_category)
    else:
        new_category = current_cat

    # 4. Description
    new_description = get_valid_string(
        "Enter new description",
        default_val=target_exp.get("description")
    )

    # Update record
    target_exp["date"] = new_date
    target_exp["amount"] = new_amount
    target_exp["category"] = new_category
    target_exp["description"] = new_description

    if save_expenses(expenses):
        print(f"\n[OK] Expense ID #{target_id} updated successfully!")
        print_table(
            headers=["ID", "Date", "Amount", "Category", "Description"],
            rows=[[str(target_id), new_date, format_currency(new_amount), new_category, new_description]],
            alignments=["^", "^", ">", "<", "<"],
        )
    else:
        print("\n[!] Failed to save updated expense to storage.")

    return expenses


def delete_expense_flow(expenses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Prompt user to delete an existing expense record by ID after confirmation.

    Args:
        expenses: Mutable list of expenses.

    Returns:
        Updated list of expenses.
    """
    print("\n" + "=" * 50)
    print("               DELETE EXPENSE")
    print("=" * 50)

    if not expenses:
        print("  No expenses available to delete.")
        return expenses

    while True:
        id_input = input("Enter Expense ID to delete (or 'c' to cancel): ").strip()
        if id_input.lower() == "c":
            return expenses

        try:
            target_id = int(id_input)
            break
        except ValueError:
            print("  [!] Please enter a valid numerical ID.")

    target_exp = next((exp for exp in expenses if exp.get("id") == target_id), None)
    if not target_exp:
        print(f"  [!] Expense with ID #{target_id} not found.")
        return expenses

    print("\nTarget Expense to Delete:")
    print_table(
        headers=["ID", "Date", "Amount", "Category", "Description"],
        rows=[[
            str(target_exp.get("id")),
            target_exp.get("date", ""),
            format_currency(target_exp.get("amount", 0.0)),
            target_exp.get("category", ""),
            target_exp.get("description", ""),
        ]],
        alignments=["^", "^", ">", "<", "<"],
    )

    confirm = get_confirmation(f"Are you sure you want to permanently delete Expense #{target_id}?", default_no=True)
    if confirm:
        expenses.remove(target_exp)
        if save_expenses(expenses):
            print(f"\n[OK] Expense #{target_id} deleted successfully.")
        else:
            print("\n[!] Failed to save changes after deletion.")
    else:
        print("\n[i] Deletion canceled.")

    return expenses


# ---------------------------------------------------------------------------
# Search, Filtering, and Sorting
# ---------------------------------------------------------------------------

def filter_by_category(expenses: list[dict[str, Any]], category: str) -> list[dict[str, Any]]:
    """Filter expenses matching a specific category (case-insensitive)."""
    return [exp for exp in expenses if exp.get("category", "").lower() == category.lower()]


def filter_by_month(expenses: list[dict[str, Any]], month_str: str) -> list[dict[str, Any]]:
    """Filter expenses matching a specific month (YYYY-MM)."""
    return [exp for exp in expenses if exp.get("date", "").startswith(month_str)]


def filter_by_date_range(
    expenses: list[dict[str, Any]],
    start_date: str,
    end_date: str
) -> list[dict[str, Any]]:
    """Filter expenses within a start and end date range (inclusive)."""
    results = []
    for exp in expenses:
        d = exp.get("date", "")
        if start_date <= d <= end_date:
            results.append(exp)
    return results


def filter_by_amount_range(
    expenses: list[dict[str, Any]],
    min_amount: float,
    max_amount: float
) -> list[dict[str, Any]]:
    """Filter expenses whose amount is between min_amount and max_amount (inclusive)."""
    return [
        exp for exp in expenses
        if min_amount <= exp.get("amount", 0.0) <= max_amount
    ]


def filter_by_keyword(expenses: list[dict[str, Any]], keyword: str) -> list[dict[str, Any]]:
    """Filter expenses whose description contains the keyword (case-insensitive)."""
    key_lower = keyword.strip().lower()
    return [
        exp for exp in expenses
        if key_lower in exp.get("description", "").lower()
    ]


def sort_expenses(
    expenses: list[dict[str, Any]],
    sort_by: str = "date",
    descending: bool = False
) -> list[dict[str, Any]]:
    """
    Return a new list of sorted expenses.

    Args:
        expenses: Input expense list.
        sort_by: 'date' or 'amount'.
        descending: True for descending order.

    Returns:
        Sorted list of expenses.
    """
    if sort_by == "amount":
        return sorted(expenses, key=lambda x: x.get("amount", 0.0), reverse=descending)
    # Default is sort by date (and ID as tiebreaker)
    return sorted(expenses, key=lambda x: (x.get("date", ""), x.get("id", 0)), reverse=descending)


def search_and_filter_flow(
    expenses: list[dict[str, Any]],
    custom_categories: set[str] | None = None
) -> None:
    """Submenu for searching, filtering, and sorting expenses."""
    while True:
        print("\n" + "=" * 50)
        print("           SEARCH & FILTER EXPENSES")
        print("=" * 50)
        print("  [1] Filter by Category")
        print("  [2] Filter by Month (YYYY-MM)")
        print("  [3] Filter by Date Range")
        print("  [4] Filter by Amount Range")
        print("  [5] Search Description by Keyword")
        print("  [6] Sort All Expenses (by Date or Amount)")
        print("  [0] Return to Main Menu")
        print("=" * 50)

        choice = get_valid_choice("Enter choice [0-6]: ", ["0", "1", "2", "3", "4", "5", "6"])

        if choice == "0":
            break

        elif choice == "1":
            cats = get_all_categories(expenses, custom_categories)
            if not cats:
                print("  No categories available.")
                continue
            print("\nSelect Category:")
            for idx, c in enumerate(cats, start=1):
                print(f"  [{idx}] {c}")
            cat_choice = int(get_valid_choice("Choose category: ", [str(i) for i in range(1, len(cats) + 1)]))
            selected_cat = cats[cat_choice - 1]
            matches = filter_by_category(expenses, selected_cat)
            view_expenses_table(matches, title=f"Expenses in Category: {selected_cat}")

        elif choice == "2":
            month = get_valid_month("Enter month (YYYY-MM)")
            matches = filter_by_month(expenses, month)
            view_expenses_table(matches, title=f"Expenses for Month: {month}")

        elif choice == "3":
            print("\nEnter Date Range:")
            start = get_valid_date("Enter start date (YYYY-MM-DD)", default_today=False)
            end = get_valid_date("Enter end date (YYYY-MM-DD)", default_today=True)
            if start > end:
                print("  [!] Start date cannot be after end date. Swapping dates automatically.")
                start, end = end, start
            matches = filter_by_date_range(expenses, start, end)
            view_expenses_table(matches, title=f"Expenses from {start} to {end}")

        elif choice == "4":
            print("\nEnter Amount Range:")
            min_amt = get_valid_amount("Enter minimum amount (₹)", allow_zero=True, default=0.0)
            max_amt = get_valid_amount("Enter maximum amount (₹)", allow_zero=False)
            if min_amt > max_amt:
                print("  [!] Minimum amount cannot exceed maximum amount. Swapping automatically.")
                min_amt, max_amt = max_amt, min_amt
            matches = filter_by_amount_range(expenses, min_amt, max_amt)
            view_expenses_table(matches, title=f"Expenses between {format_currency(min_amt)} and {format_currency(max_amt)}")

        elif choice == "5":
            kw = get_valid_string("Enter search keyword").strip()
            matches = filter_by_keyword(expenses, kw)
            view_expenses_table(matches, title=f"Search Results for '{kw}'")

        elif choice == "6":
            print("\nSort by:")
            print("  [1] Date (Newest first)")
            print("  [2] Date (Oldest first)")
            print("  [3] Amount (Highest first)")
            print("  [4] Amount (Lowest first)")
            sort_opt = get_valid_choice("Choose sort option [1-4]: ", ["1", "2", "3", "4"])
            if sort_opt == "1":
                sorted_list = sort_expenses(expenses, sort_by="date", descending=True)
                view_expenses_table(sorted_list, title="Expenses Sorted by Date (Newest First)")
            elif sort_opt == "2":
                sorted_list = sort_expenses(expenses, sort_by="date", descending=False)
                view_expenses_table(sorted_list, title="Expenses Sorted by Date (Oldest First)")
            elif sort_opt == "3":
                sorted_list = sort_expenses(expenses, sort_by="amount", descending=True)
                view_expenses_table(sorted_list, title="Expenses Sorted by Amount (Highest First)")
            elif sort_opt == "4":
                sorted_list = sort_expenses(expenses, sort_by="amount", descending=False)
                view_expenses_table(sorted_list, title="Expenses Sorted by Amount (Lowest First)")

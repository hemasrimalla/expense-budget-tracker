"""
Personal Expense & Budget Tracker.

Main CLI Entry Point providing an interactive menu-driven interface to track expenses,
manage category and monthly budgets, generate spending reports, and export to CSV.
"""

from pathlib import Path
import sys

from budget_manager import budget_menu_flow
from expense_manager import (
    DEFAULT_CATEGORIES,
    add_expense_flow,
    delete_expense_flow,
    edit_expense_flow,
    get_all_categories,
    search_and_filter_flow,
    view_expenses_table,
)
from reports import reports_menu_flow
from storage import (
    BUDGETS_FILE,
    DATA_DIR,
    EXPENSES_FILE,
    export_expenses_to_csv,
    load_budgets,
    load_expenses,
)
from utils import (
    format_currency,
    get_confirmation,
    get_valid_choice,
    get_valid_string,
    pause_for_user,
    print_table,
)


def display_welcome_banner() -> None:
    """Print the welcome header banner."""
    print("=" * 65)
    print("       PERSONAL EXPENSE & BUDGET TRACKER (v1.0)")
    print("       Take control of your finances, one rupee at a time")
    print("=" * 65)


def display_main_menu() -> None:
    """Display the primary CLI options."""
    print("\n" + "-" * 45)
    print("                 MAIN MENU")
    print("-" * 45)
    print("  [1] Add New Expense")
    print("  [2] View All Expenses")
    print("  [3] Edit an Expense")
    print("  [4] Delete an Expense")
    print("  [5] Search & Filter Expenses")
    print("  [6] Manage Budgets (Monthly & Category)")
    print("  [7] Spending Reports & Analytics")
    print("  [8] Export Expenses to CSV")
    print("  [9] Manage Categories")
    print("  [0] Exit Application")
    print("-" * 45)


def category_management_flow(
    expenses: list[dict],
    custom_categories: set[str]
) -> set[str]:
    """Submenu for viewing and adding custom categories."""
    while True:
        all_cats = get_all_categories(expenses, custom_categories)
        print("\n" + "=" * 50)
        print("             CATEGORY MANAGEMENT")
        print("=" * 50)
        print("Current Active Categories:")
        for idx, cat in enumerate(all_cats, start=1):
            tag = " (Custom)" if cat in custom_categories or cat not in DEFAULT_CATEGORIES else ""
            print(f"  {idx:2d}. {cat}{tag}")

        print("\n  [1] Add New Custom Category")
        print("  [0] Return to Main Menu")

        sub_choice = get_valid_choice("Enter choice [0-1]: ", ["0", "1"])
        if sub_choice == "0":
            break
        elif sub_choice == "1":
            new_cat = get_valid_string("Enter new category name: ").strip().title()
            if not new_cat:
                print("  [!] Category name cannot be empty.")
            elif new_cat in all_cats:
                print(f"  [i] Category '{new_cat}' already exists.")
            else:
                custom_categories.add(new_cat)
                print(f"  [OK] Custom category '{new_cat}' added successfully!")
    return custom_categories


def export_csv_flow(expenses: list[dict]) -> None:
    """Prompt user and export expenses to a CSV file."""
    print("\n" + "=" * 50)
    print("              EXPORT TO CSV")
    print("=" * 50)

    if not expenses:
        print("  [!] No expenses to export.")
        return

    default_filename = "expenses_export.csv"
    default_path = DATA_DIR / default_filename

    filename_input = input(f"Enter destination filename or path [default: data/{default_filename}]: ").strip()
    if filename_input:
        target_path = Path(filename_input)
    else:
        target_path = default_path

    if export_expenses_to_csv(expenses, target_path):
        print(f"\n[OK] Successfully exported {len(expenses)} expenses to:")
        print(f"     {target_path.resolve()}")
    else:
        print("\n[!] Failed to export to CSV.")


def main() -> None:
    """Main application loop."""
    display_welcome_banner()

    # Load persistent data
    expenses = load_expenses(EXPENSES_FILE)
    budgets = load_budgets(BUDGETS_FILE)

    # Initialize custom categories from existing data
    custom_categories: set[str] = set()
    for exp in expenses:
        cat = exp.get("category")
        if cat and cat not in DEFAULT_CATEGORIES:
            custom_categories.add(cat)

    print(f"Loaded {len(expenses)} expenses and {len(budgets)} monthly budget configurations.\n")

    while True:
        try:
            display_main_menu()
            choice = get_valid_choice("Select an option [0-9]: ", [str(i) for i in range(10)])

            if choice == "1":
                expenses = add_expense_flow(expenses, budgets, custom_categories)
                pause_for_user()

            elif choice == "2":
                view_expenses_table(expenses, title="All Recorded Expenses")
                pause_for_user()

            elif choice == "3":
                expenses = edit_expense_flow(expenses, custom_categories)
                pause_for_user()

            elif choice == "4":
                expenses = delete_expense_flow(expenses)
                pause_for_user()

            elif choice == "5":
                search_and_filter_flow(expenses, custom_categories)
                pause_for_user()

            elif choice == "6":
                budgets = budget_menu_flow(budgets, expenses, custom_categories)

            elif choice == "7":
                reports_menu_flow(expenses)
                pause_for_user()

            elif choice == "8":
                export_csv_flow(expenses)
                pause_for_user()

            elif choice == "9":
                custom_categories = category_management_flow(expenses, custom_categories)

            elif choice == "0":
                confirm_exit = get_confirmation("Are you sure you want to exit?", default_no=False)
                if confirm_exit:
                    print("\nThank you for using Personal Expense & Budget Tracker. Goodbye!\n")
                    sys.exit(0)

        except KeyboardInterrupt:
            print("\n\nOperation interrupted by user.")
            if get_confirmation("Exit application?", default_no=True):
                print("Goodbye!")
                sys.exit(0)
        except Exception as err:
            print(f"\n[!] Unexpected error encountered: {err}")
            pause_for_user("Press Enter to continue...")


if __name__ == "__main__":
    main()

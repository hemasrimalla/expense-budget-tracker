"""
Storage Module for Personal Expense & Budget Tracker.

Handles JSON persistence for expenses and budgets, automatic recovery from
missing or corrupted files, and CSV export functionality using Python standard library.
"""

import csv
from datetime import datetime
import json
import os
from pathlib import Path
from typing import Any

# Default storage paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPENSES_FILE = DATA_DIR / "expenses.json"
BUDGETS_FILE = DATA_DIR / "budgets.json"


def ensure_data_dir(directory: Path = DATA_DIR) -> None:
    """Ensure the target storage directory exists."""
    directory.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Expenses Storage (JSON)
# ---------------------------------------------------------------------------

def load_expenses(filepath: Path = EXPENSES_FILE) -> list[dict[str, Any]]:
    """
    Load expenses from a JSON file.

    Recovers gracefully if the file is missing or corrupted.
    If corrupted, the corrupt file is backed up before initializing a new empty list.

    Args:
        filepath: Path to the expenses JSON file.

    Returns:
        List of expense dictionaries.
    """
    ensure_data_dir(filepath.parent)

    if not filepath.exists():
        return []

    try:
        with open(filepath, mode="r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                print(f"  [!] Warning: {filepath.name} does not contain a list. Resetting gracefully.")
                _backup_corrupted_file(filepath)
                return []
    except json.JSONDecodeError as err:
        print(f"  [!] Warning: Corrupted JSON detected in {filepath.name} ({err}).")
        _backup_corrupted_file(filepath)
        return []
    except OSError as err:
        print(f"  [!] Error reading {filepath.name}: {err}")
        return []


def save_expenses(expenses: list[dict[str, Any]], filepath: Path = EXPENSES_FILE) -> bool:
    """
    Save the list of expenses to a JSON file.

    Args:
        expenses: List of expense dictionaries.
        filepath: Path to the target JSON file.

    Returns:
        True if successfully saved, False otherwise.
    """
    ensure_data_dir(filepath.parent)
    try:
        # Write to a temporary file first then replace for atomic persistence
        temp_file = filepath.with_suffix(".tmp")
        with open(temp_file, mode="w", encoding="utf-8") as f:
            json.dump(expenses, f, indent=2, ensure_ascii=False)
        temp_file.replace(filepath)
        return True
    except OSError as err:
        print(f"  [!] Error saving expenses to {filepath.name}: {err}")
        return False


# ---------------------------------------------------------------------------
# Budgets Storage (JSON)
# ---------------------------------------------------------------------------

def load_budgets(filepath: Path = BUDGETS_FILE) -> dict[str, Any]:
    """
    Load budgets from a JSON file.

    Structure:
    {
        "YYYY-MM": {
            "total_budget": float,
            "category_budgets": {
                "CategoryName": float
            }
        }
    }

    Args:
        filepath: Path to the budgets JSON file.

    Returns:
        Dictionary of monthly budgets.
    """
    ensure_data_dir(filepath.parent)

    if not filepath.exists():
        return {}

    try:
        with open(filepath, mode="r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            else:
                print(f"  [!] Warning: {filepath.name} does not contain a valid budget dictionary.")
                _backup_corrupted_file(filepath)
                return {}
    except json.JSONDecodeError as err:
        print(f"  [!] Warning: Corrupted JSON detected in {filepath.name} ({err}).")
        _backup_corrupted_file(filepath)
        return {}
    except OSError as err:
        print(f"  [!] Error reading {filepath.name}: {err}")
        return {}


def save_budgets(budgets: dict[str, Any], filepath: Path = BUDGETS_FILE) -> bool:
    """
    Save monthly budgets to a JSON file.

    Args:
        budgets: Budget dictionary.
        filepath: Path to the target JSON file.

    Returns:
        True if successfully saved, False otherwise.
    """
    ensure_data_dir(filepath.parent)
    try:
        temp_file = filepath.with_suffix(".tmp")
        with open(temp_file, mode="w", encoding="utf-8") as f:
            json.dump(budgets, f, indent=2, ensure_ascii=False)
        temp_file.replace(filepath)
        return True
    except OSError as err:
        print(f"  [!] Error saving budgets to {filepath.name}: {err}")
        return False


# ---------------------------------------------------------------------------
# CSV Export
# ---------------------------------------------------------------------------

def export_expenses_to_csv(expenses: list[dict[str, Any]], output_filepath: Path | str) -> bool:
    """
    Export list of expenses to a CSV file.

    Args:
        expenses: List of expense dictionaries.
        output_filepath: Destination CSV file path.

    Returns:
        True if export succeeded, False otherwise.
    """
    path = Path(output_filepath)
    ensure_data_dir(path.parent)

    fieldnames = ["ID", "Date", "Amount", "Category", "Description"]

    try:
        with open(path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for exp in expenses:
                writer.writerow({
                    "ID": exp.get("id", ""),
                    "Date": exp.get("date", ""),
                    "Amount": f"{exp.get('amount', 0.0):.2f}",
                    "Category": exp.get("category", ""),
                    "Description": exp.get("description", "")
                })
        return True
    except OSError as err:
        print(f"  [!] Failed to export expenses to CSV: {err}")
        return False


# ---------------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------------

def _backup_corrupted_file(filepath: Path) -> None:
    """Rename a corrupted file with a timestamped suffix for recovery inspection."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    corrupt_backup = filepath.with_name(f"{filepath.stem}_corrupted_{timestamp}{filepath.suffix}")
    try:
        filepath.replace(corrupt_backup)
        print(f"  [i] Corrupted file preserved as: {corrupt_backup.name}")
    except OSError:
        pass

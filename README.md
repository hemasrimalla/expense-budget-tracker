# Personal Expense & Budget Tracker

A feature-rich, interactive CLI application built with pure Python 3.10+ standard libraries to track personal finances, manage monthly and category-specific budgets, monitor spending habits, and export financial summaries.

---

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Installation & How to Run](#installation--how-to-run)
- [Menu Overview](#menu-overview)
- [Sample Usage & Output](#sample-usage--output)
- [Data Storage & Formats](#data-storage--formats)
- [Error Handling & Edge Cases](#error-handling--edge-cases)
- [Future Improvements](#future-improvements)

---

## Overview

The **Personal Expense & Budget Tracker** is designed to strengthen core Python skills:
- **Modular Programming**: Separation of concerns across storage, calculations, UI, and utilities.
- **Data Structures**: Effective use of lists, dictionaries, tuples, and sets.
- **File Handling**: JSON serialization and persistence with atomic file writes and automatic corrupted-file recovery, plus CSV export.
- **Date & Time Operations**: Parsing, formatting, date comparisons, and calendar-aware daily average calculations.
- **Defensive Programming**: Robust exception handling for invalid numeric values, negative amounts, bad dates, empty inputs, and missing files.
- **Zero External Dependencies**: Powered entirely by the Python Standard Library (`csv`, `json`, `datetime`, `calendar`, `os`, `pathlib`).

---

## Key Features

1. **Expense Tracking (CRUD)**:
   - Add new expenses with unique incremental IDs, dates (YYYY-MM-DD, defaults to today), positive amounts, category selection, and descriptions.
   - View all recorded expenses formatted in an aligned ASCII table with currency (`₹`) and total summaries.
   - Edit any existing expense field (date, amount, category, note) with the option to press Enter to keep current values.
   - Delete expenses with confirmation.

2. **Category Management**:
   - Predefined categories: `Food`, `Transport`, `Rent`, `Bills`, `Shopping`, `Health`, `Entertainment`, `Other`.
   - Ability to dynamically add custom categories on the fly.

3. **Monthly & Category Budgeting**:
   - Set an overall monthly budget and optional category-specific budgets for any month (`YYYY-MM`).
   - Visual ASCII progress bar (`[█████████████████░░░] 85.0%`).
   - Intelligent status indicators:
     - `[OK]` when utilization is below 80%.
     - `[WARNING]` alert when spending reaches or exceeds 80%.
     - `[EXCEEDED]` alert when spending crosses 100%, reporting exact overage amounts.
   - Instant inline alert whenever an added expense pushes a monthly or category budget past 80% or 100%.

4. **Spending Reports & Analytics**:
   - **Monthly Summary**: Total spend, transaction count, average per transaction, calendar-aware daily average spend, highest/lowest spending categories, and largest single expense.
   - **Category Distribution Chart**: Horizontal ASCII proportion bars (`███████░░░░░░░░`) and percentage breakdowns.
   - **Month-over-Month Comparison**: Chronological tracking across months with percentage change calculations.
   - **All-Time Category Breakdown**: Cumulative view of spending habits over time.

5. **Search & Multi-Criteria Filtering**:
   - Filter by Category.
   - Filter by Month (`YYYY-MM`).
   - Filter by Date Range (`Start Date` to `End Date`).
   - Filter by Amount Range (`Min Amount` to `Max Amount`).
   - Search by Keyword in Description (case-insensitive).
   - Multi-directional sorting (Date Newest/Oldest, Amount Highest/Lowest).

6. **Persistence & CSV Export**:
   - Data stored reliably in `data/expenses.json` and `data/budgets.json`.
   - Export expense records to CSV at any chosen path.

---

## Project Structure

```
expense-budget-tracker/
├── main.py              # Menu-driven CLI entry point and main workflow loop
├── expense_manager.py   # CRUD operations, category selector, filtering & sorting
├── budget_manager.py    # Monthly/category budget calculations, thresholds & alerts
├── reports.py           # Monthly summaries, analytics, charts & MoM comparisons
├── storage.py           # Atomic JSON persistence, corruption recovery & CSV export
├── utils.py             # Validation (dates, amounts, strings), currency & table formatting
├── data/
│   ├── expenses.json    # Persistent JSON storage for expense items
│   └── budgets.json     # Persistent JSON storage for monthly budgets
├── sample_output/
│   ├── cli_session_walkthrough.txt  # Full interactive CLI session log
│   ├── budget_report_sample.txt     # Sample budget status and alert outputs
│   └── spending_report_sample.txt   # Sample monthly spending summary and comparison
└── README.md            # Comprehensive documentation
```

---

## Installation & How to Run

### Prerequisites
- Python 3.10 or higher installed on your system.
- Standard terminal (PowerShell, Command Prompt, bash, zsh, etc.).

### Running the Application

1. Clone or navigate to the project directory:
   ```bash
   cd expense-budget-tracker
   ```

2. Run the application:
   ```bash
   python main.py
   ```

The application ships with a pre-seeded sample dataset in `data/expenses.json` and `data/budgets.json`, allowing you to immediately explore all features without manual data entry.

---

## Menu Overview

```text
---------------------------------------------
                 MAIN MENU
---------------------------------------------
  [1] Add New Expense
  [2] View All Expenses
  [3] Edit an Expense
  [4] Delete an Expense
  [5] Search & Filter Expenses
  [6] Manage Budgets (Monthly & Category)
  [7] Spending Reports & Analytics
  [8] Export Expenses to CSV
  [9] Manage Categories
  [0] Exit Application
---------------------------------------------
```

---

## Sample Usage & Output

### 1. Viewing All Expenses
```text
+----+------------+------------+---------------+-----------------------------------+
| ID |    Date    |     Amount | Category      | Description                       |
+----+------------+------------+---------------+-----------------------------------+
| 10 | 2026-11-01 | ₹12,000.00 | Rent          | November Apartment Rent           |
| 11 | 2026-11-02 |  ₹1,550.00 | Bills         | Electricity bill payment          |
| 12 | 2026-11-04 |  ₹2,450.00 | Food          | Monthly pantry grocery refill     |
| 13 | 2026-11-05 |    ₹420.00 | Transport     | Cab ride to railway station       |
| 14 | 2026-11-07 |  ₹3,800.00 | Shopping      | Ergonomic desk chair              |
| 15 | 2026-11-08 |    ₹950.00 | Health        | Vitamins & medical supplies       |
| 16 | 2026-11-09 |  ₹2,850.00 | Food          | Weekend dining out                |
| 17 | 2026-11-10 |  ₹1,480.00 | Other         | Annual cloud storage subscription |
+----+------------+------------+---------------+-----------------------------------+
 Total Expenses: 17 | Total Spent: ₹51,650.00
```

### 2. Monthly Budget Status & Warnings
```text
=================================================================
                        BUDGET STATUS FOR 2026-11                
=================================================================

Total Budget : ₹30,000.00
Total Spent  : ₹25,500.00
Remaining    : ₹4,500.00
Utilization  : [█████████████████░░░] 85.0%
Status       : [!] WARNING: 80%+ Utilized (85.0% of budget consumed)

Category-wise Budget Breakdown:
+-----------+------------+------------+-----------+--------+-----------+
| Category  |     Budget |      Spent | Remaining | Used % |   Status  |
+-----------+------------+------------+-----------+--------+-----------+
| Bills     |  ₹2,000.00 |  ₹1,550.00 |   ₹450.00 |  77.5% |     OK    |
| Food      |  ₹6,000.00 |  ₹5,300.00 |   ₹700.00 |  88.3% |  WARNING  |
| Health    |  No Budget |    ₹950.00 |         - |      - | Untracked |
| Other     |  No Budget |  ₹1,480.00 |         - |      - | Untracked |
| Rent      | ₹12,000.00 | ₹12,000.00 |     ₹0.00 | 100.0% |  WARNING  |
| Shopping  |  ₹3,500.00 |  ₹3,800.00 |  -₹300.00 | 108.6% |  EXCEEDED |
| Transport |  ₹1,000.00 |    ₹420.00 |   ₹580.00 |  42.0% |     OK    |
+-----------+------------+------------+-----------+--------+-----------+
```

### 3. Monthly Spending Report & Visual Distribution
```text
=================================================================
                     MONTHLY SPENDING REPORT: 2026-11            
=================================================================

  • Total Amount Spent    : ₹25,500.00
  • Total Transactions    : 8
  • Average per Expense   : ₹3,187.50
  • Average Daily Spend   : ₹2,550.00 (based on 10 days elapsed in current month)
  • Top Spending Category : Rent (₹12,000.00 - 47.1%)
  • Lowest Category       : Transport (₹420.00)
  • Largest Single Expense: ₹12,000.00 (November Apartment Rent on 2026-11-01)

--- Category Breakdown ---
+-----------+-------------+------------+-------+-----------------+
| Category  | Total Spent | % of Month | Count | Distribution    |
+-----------+-------------+------------+-------+-----------------+
| Rent      |  ₹12,000.00 |      47.1% |   1   | ███████░░░░░░░░ |
| Food      |   ₹5,300.00 |      20.8% |   2   | ███░░░░░░░░░░░░ |
| Shopping  |   ₹3,800.00 |      14.9% |   1   | ██░░░░░░░░░░░░░ |
| Bills     |   ₹1,550.00 |       6.1% |   1   | █░░░░░░░░░░░░░░ |
| Other     |   ₹1,480.00 |       5.8% |   1   | █░░░░░░░░░░░░░░ |
| Health    |     ₹950.00 |       3.7% |   1   | █░░░░░░░░░░░░░░ |
| Transport |     ₹420.00 |       1.6% |   1   | ░░░░░░░░░░░░░░░ |
+-----------+-------------+------------+-------+-----------------+
```

### 4. Month-over-Month Comparison
```text
+---------+-------------+--------------+--------------+------------+
|  Month  | Total Spent | Transactions | Top Category | MoM Change |
+---------+-------------+--------------+--------------+------------+
| 2026-10 |  ₹26,150.00 |      9       | Rent         |   Baseline |
| 2026-11 |  ₹25,500.00 |      8       | Rent         |      -2.5% |
+---------+-------------+--------------+--------------+------------+
```

---

## Data Storage & Formats

### `data/expenses.json`
Stores the complete list of all transactions:
```json
[
  {
    "id": 1,
    "date": "2026-11-01",
    "amount": 12000.0,
    "category": "Rent",
    "description": "November Apartment Rent"
  }
]
```

### `data/budgets.json`
Stores monthly budgets and optional category targets:
```json
{
  "2026-11": {
    "total_budget": 30000.0,
    "category_budgets": {
      "Rent": 12000.0,
      "Food": 6000.0,
      "Shopping": 3500.0,
      "Bills": 2000.0,
      "Transport": 1000.0
    }
  }
}
```

### `data/expenses_export.csv`
Export format compatible with Excel, Google Sheets, or LibreOffice:
```csv
ID,Date,Amount,Category,Description
1,2026-10-02,12000.00,Rent,October Apartment Rent
2,2026-10-04,1450.00,Bills,Electricity & Water Bill
```

---

## Error Handling & Edge Cases

The application includes exhaustive defensive programming patterns:
- **Corrupted JSON Recovery**: If `expenses.json` or `budgets.json` is corrupted or edited with invalid syntax, the loader detects `json.JSONDecodeError`, archives the corrupted file to a timestamped backup (e.g. `expenses_corrupted_20261110_150427.json`), and reinitializes cleanly without crashing.
- **Negative & Non-numeric Inputs**: All numeric prompts reject negative values, strings, or zero (when prohibited), stripping commas and handling decimals cleanly.
- **Invalid Dates**: Verifies `YYYY-MM-DD` syntax and calendar validity (e.g. rejects `2026-02-31`), handling leap years and century constraints.
- **Date Inversions**: When searching by date range or amount range, if the start value exceeds the end value, the application automatically swaps them and informs the user.
- **Keyboard Interrupts**: Captures `Ctrl+C` gracefully and prompts for clean exit instead of showing a raw Python traceback.

---

## Future Improvements

- **Recurring Expenses**: Automatically schedule recurring monthly expenses like subscriptions and rent.
- **Multi-Currency Support**: Currency converter supporting USD, EUR, GBP alongside INR (₹).
- **Export to PDF / HTML**: Generate visual PDF reports with charts using reportlab or HTML templates.
- **Interactive Visualizations**: Graphical dashboard using Tkinter or web interface (Flask / FastAPI).
- **Receipt OCR**: Extract amount, vendor, and date from receipt images.

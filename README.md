# Personal Expense Tracker

A full-stack expense tracker: register, organize spending into categories
(with optional monthly budgets), log expenses, filter/search/export them,
and see a monthly dashboard (totals with month-over-month change, category
breakdown with budget progress, 6-month trend, recent activity).

**Stack:** Python/Flask, MySQL (SQLAlchemy ORM), session-cookie auth
(Flask-Login), server-rendered Jinja templates styled with Tailwind (CDN),
vanilla JS for small interactive touches (dark mode, mobile nav, delete
confirmations, debounced search, charts). No frontend framework, no npm
build step.

## Project layout

```
app/
  auth/          register / login / logout
  account/        profile + password settings
  categories/     category CRUD + budgets
  expenses/       expense CRUD + filtering + CSV export
  dashboard/      aggregated summary view
  utils.py        shared month-bounds helpers
  models.py       User, Category, Expense (+ relationships)
  templates/, static/
schema.sql        CREATE TABLE statements (run once against MySQL)
tests/            pytest suite (needs a real MySQL test database)
```

## Setup

### 1. Prerequisites

- Python 3.11+
- A running MySQL server (8.x recommended) you have credentials for

### 2. Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate      # macOS/Linux
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env.example` to `.env` and fill in your real values:

```bash
copy .env.example .env           # Windows
# cp .env.example .env            # macOS/Linux
```

```
SECRET_KEY=<any random string>
DB_HOST=localhost
DB_PORT=3306
DB_USER=<your MySQL user>
DB_PASSWORD=<your MySQL password>
DB_NAME=expense_tracker
TEST_DB_NAME=expense_tracker_test   # only needed to run pytest
```

Both `DB_NAME` and `TEST_DB_NAME` must already exist as empty databases on
your MySQL server — the app doesn't create them for you:

```sql
CREATE DATABASE expense_tracker;
CREATE DATABASE expense_tracker_test;   -- only needed to run pytest
```

### 4. Create the schema

```bash
mysql -u <user> -p expense_tracker < schema.sql
mysql -u <user> -p expense_tracker_test < schema.sql   -- only needed to run pytest
```

**Already set up the database before?** `schema.sql` now includes a
`monthly_budget` column on `categories` (used by the budgets feature) that
didn't exist in the original schema. `CREATE TABLE IF NOT EXISTS` won't add
it to a table that already exists, so run this once against both databases
instead of re-running `schema.sql`:

```sql
ALTER TABLE categories ADD COLUMN monthly_budget DECIMAL(10, 2) NULL;
```

### 5. Run the app

```bash
flask --app wsgi run
```

Visit `http://127.0.0.1:5000`.

### 6. Run the automated tests (optional)

```bash
pytest
```

The suite runs against `TEST_DB_NAME`, not your real data.

## Manual test checklist

Work through this after setup to confirm everything works end-to-end.

**Auth**
- [ ] Register a new account — you land on the dashboard, logged in
- [ ] Register again with the same email — rejected with a clear error
- [ ] Log out — redirected to login
- [ ] Log in with the wrong password — rejected with a clear error
- [ ] Log in with correct credentials — lands on the dashboard
- [ ] While logged out, visit `/expenses/`, `/categories/`, or `/` directly — redirected to login

**Categories**
- [ ] After registering, seven default categories already exist (Food, Transport, Housing, Utilities, Entertainment, Health, Other)
- [ ] Create a new category — appears in the list
- [ ] Create a category with a name you already have — rejected with a clear error
- [ ] Edit a category's name — updates in place
- [ ] Delete a category that has no expenses — removed
- [ ] Try to delete a category that has expenses — blocked with an explanatory message, category still there
- [ ] Set a monthly budget on a category — a progress bar appears showing this month's spend against it
- [ ] Add expenses past the budget — the bar switches color and shows "Over budget"
- [ ] Leave the budget field blank — no progress bar shown for that category

**Expenses**
- [ ] Add an expense (amount, category, date, description) — appears in the expense list and reflects on the dashboard
- [ ] Edit an expense — changes reflected in the list
- [ ] Delete an expense — removed from the list
- [ ] Filter the expense list by category — only matching expenses show
- [ ] Filter by month — only expenses in that month show
- [ ] Search by description text — only matching expenses show
- [ ] Clear filters — full list returns
- [ ] Add 20+ expenses and confirm pagination controls appear and work
- [ ] Click "Export CSV" with no filters — downloads a CSV with all your expenses
- [ ] Apply a filter, then export — the CSV only contains the filtered rows

**Dashboard**
- [ ] With no expenses yet, dashboard shows an empty state with a call to action
- [ ] Month total matches the sum of that month's expenses
- [ ] The month total shows a "New" badge when there's no prior-month data, or a percentage badge (colored/arrowed up or down) once a previous month has expenses to compare against
- [ ] Spend-by-category chart/list matches the actual per-category totals for the month, with a budget progress bar where a budget is set
- [ ] Navigate to the previous/next month — total and breakdown update accordingly
- [ ] 6-month trend chart shows a bar per month with sensible totals
- [ ] Recent expenses list shows your most recent entries, newest first (independent of the month you're viewing)

**Account**
- [ ] Update your name/email from the Account page — reflected immediately
- [ ] Try changing your email to one already used by another account — rejected with a clear error
- [ ] Change your password with the wrong current password — rejected with a clear error
- [ ] Change your password correctly, log out, log back in with the new password — works

**Appearance**
- [ ] Toggle dark mode from the sidebar — the whole app switches themes, and the choice survives a page refresh
- [ ] Resize the browser to a narrow/mobile width — the sidebar collapses behind a hamburger menu that opens/closes correctly
- [ ] Charts and progress bars remain legible in both light and dark mode

**General**
- [ ] Refresh any page — session persists (still logged in) via the session cookie
- [ ] Try accessing another user's expense/category URL directly (e.g. by guessing an ID) while logged in as a different user — you get a 404, not their data

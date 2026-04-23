# Accounting App

Minimal double-entry bookkeeping web application built with Python, Pydantic, and Streamlit.

## Architecture

```
domain/          pure business logic, no framework dependencies
  accounts.py    fixed chart of accounts
  partner.py     Partner entity (pydantic, frozen)
  journal.py     JournalEntry aggregate + JournalLine value object
  posting.py     PostingRules domain service
  interfaces.py  abstract PartnerRepository, JournalRepository

application/     use cases, depend only on domain interfaces
  commands.py    validated command DTOs (pydantic)
  use_cases.py   PostCustomerInvoice, PostVendorBill, PostPayment, AddPartner
  reports.py     PnLQuery, PartnerLedgerQuery (read side)

infrastructure/  concrete implementations
  database.py    SQLite schema and connection
  repositories.py SQLitePartnerRepository, SQLiteJournalRepository

tests/
  fakes/         InMemoryPartnerRepository, InMemoryJournalRepository
  unit/domain/   aggregate and posting rule tests (no DB)
  unit/application/ use case tests via in-memory repos
```

## Fixed Chart of Accounts

| Code | Name                  | Type      | Normal Balance |
|------|-----------------------|-----------|----------------|
| 1000 | Cash                  | Asset     | Debit          |
| 1100 | Accounts Receivable   | Asset     | Debit          |
| 2000 | Accounts Payable      | Liability | Credit         |
| 4000 | Revenue               | Revenue   | Credit         |
| 5000 | Expense               | Expense   | Debit          |

## Business Flows

| Event             | Debit        | Credit       |
|-------------------|--------------|--------------|
| Customer Invoice  | 1100 AR      | 4000 Revenue |
| Customer Payment  | 1000 Cash    | 1100 AR      |
| Vendor Bill       | 5000 Expense | 2000 AP      |
| Vendor Payment    | 2000 AP      | 1000 Cash    |

## Run with Docker

```bash
docker build -t accounting-app .
docker run -p 8501:8501 -v $(pwd)/data:/app/data accounting-app
```

Open http://localhost:8501

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run tests

```bash
pytest tests/ -v
```

## Technical decisions

- **SQLite** — no infrastructure needed, file-based persistence, volume-mounted in Docker
- **Pydantic v2** — validation at the boundary (commands), immutable value objects in domain
- **Double-entry invariant** — `JournalEntry.assert_balanced()` is called by `PostingRules` before any persistence
- **No ORM** — plain `sqlite3` for clarity and full control over SQL
- **In-memory repos for tests** — use cases are testable without a database
- **`@st.cache_resource`** — single shared SQLite connection across Streamlit pages

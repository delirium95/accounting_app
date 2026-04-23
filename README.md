# Accounting App

Minimal double-entry bookkeeping web application built with Python, Pydantic, and Streamlit.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501

## Run with Docker

```bash
docker build -t accounting-app .
docker run -p 8501:8501 -v $(pwd)/data:/app/data accounting-app
```

Open http://localhost:8501

## Run tests

```bash
pytest tests/ -v
```

---

## Architecture

```
domain/               pure business logic, zero framework dependencies
  accounts.py         fixed chart of accounts + account constants
  partner.py          Partner entity (pydantic, frozen)
  journal.py          JournalEntry aggregate root + JournalLine value object
  posting.py          PostingRules domain service
  interfaces.py       abstract PartnerRepository, JournalRepository (ABC)
  exceptions.py       DomainError hierarchy (PartnerNotFoundError, etc.)
  types.py            NewType aliases: PartnerId, EntryId, AccountCode

application/          use cases, depend only on domain interfaces
  commands.py         validated command DTOs (pydantic)
  use_cases.py        AddPartner, PostCustomerInvoice, PostVendorBill, PostPayment
  reports.py          PnLQuery, PartnerLedgerQuery (read side)

infrastructure/       concrete implementations
  database.py         SQLite connection, WAL mode, schema init
  repositories.py     SQLitePartnerRepository, SQLiteJournalRepository

presentation/         MVC presentation layer
  base.py             BaseController(ABC), BaseView(ABC)
  controllers/        orchestrate use cases, prepare data for views
  views/              Streamlit rendering only — zero business logic
  views/shared.py     reusable UI components (tables, inputs)

pages/                Streamlit multipage entry points (5-line wiring each)

tests/
  fakes/              InMemoryPartnerRepository, InMemoryJournalRepository
  unit/domain/        aggregate and posting rule tests (no DB)
  unit/application/   use case tests via in-memory repos
```

## Fixed Chart of Accounts

| Code | Name                | Type      | Normal Balance |
|------|---------------------|-----------|----------------|
| 1000 | Cash                | Asset     | Debit          |
| 1100 | Accounts Receivable | Asset     | Debit          |
| 2000 | Accounts Payable    | Liability | Credit         |
| 4000 | Revenue             | Revenue   | Credit         |
| 5000 | Expense             | Expense   | Debit          |

## Business Flows

| Event            | Debit        | Credit       |
|------------------|--------------|--------------|
| Customer Invoice | 1100 AR      | 4000 Revenue |
| Customer Payment | 1000 Cash    | 1100 AR      |
| Vendor Bill      | 5000 Expense | 2000 AP      |
| Vendor Payment   | 2000 AP      | 1000 Cash    |

## Technical Decisions

- **SQLite** — file-based persistence, no infrastructure needed, volume-mounted in Docker
- **Pydantic v2** — validation at the boundary (commands), immutable value objects in domain (`frozen=True`)
- **Double-entry invariant** — `JournalEntry.assert_balanced()` enforced by `PostingRules` before any persistence
- **No ORM** — plain `sqlite3` for full control over SQL; single atomic transaction per journal entry
- **DDD layering** — domain has zero imports from application, infrastructure, or presentation
- **MVC in presentation** — `BaseController(ABC)` / `BaseView(ABC)` hierarchy; ISP respected (each controller takes only the repos it needs)
- **Custom exceptions** — `DomainError` base with typed subclasses; no raw `ValueError` escaping domain boundary
- **In-memory repos for tests** — use cases fully testable without a database
- **`@st.cache_resource`** — single shared SQLite connection across all Streamlit pages

# Prompt History

Prompts used with Claude (claude-sonnet-4-6) during development of this task.

---

## 1 — Domain design

**Prompt:**
> I need to build a minimal accounting web app with Streamlit. Fixed accounts: 1000 Cash, 1100 AR, 2000 AP, 4000 Revenue, 5000 Expense. What are the core business events and how should double-entry posting rules map to them?

**Used:** Identified four core flows (customer invoice, customer payment, vendor bill, vendor payment) and their debit/credit pairs. Confirmed that every posting must be balanced before persistence.

---

## 2 — Architecture

**Prompt:**
> Design a layered DDD architecture for this app. Domain layer should have no framework dependencies. Use repository pattern with abstract interfaces. Use cases orchestrate domain. Infrastructure holds SQLite implementations. What patterns fit here?

**Used:** Domain → Application → Infrastructure layering. `JournalEntry` as aggregate root with balance invariant. `PostingRules` as domain service. Abstract `JournalRepository` and `PartnerRepository` interfaces. In-memory fakes for tests.

---

## 3 — Pydantic value objects

**Prompt:**
> Should I use pydantic BaseModel with frozen=True for domain value objects like JournalLine and JournalEntry? What are the tradeoffs vs plain dataclasses?

**Used:** Pydantic for all domain models — gives field-level validation, `model_copy(update=...)` for persistence return values, and consistency with the codebase. `frozen=True` enforces immutability on value objects.

---

## 4 — JournalEntry aggregate invariant

**Prompt:**
> How should I enforce that a JournalEntry is always balanced (total debit == total credit)? Should the validation happen in the aggregate or in the posting rules?

**Used:** Validation in both places — `PostingRules` calls `entry.assert_balanced()` before returning, which is a defensive check. The aggregate exposes `is_balanced` as a property for tests to assert on.

---

## 5 — Partner ledger balance logic

**Prompt:**
> For the partner ledger, how should I calculate the outstanding balance for customers vs vendors? The accounting direction differs between AR and AP.

**Used:** 
- Customer AR balance: `debit - credit` (invoice = debit, payment = credit → positive = they owe us)
- Vendor AP balance: `credit - debit` (bill = credit, payment = debit → positive = we owe them)

---

## 6 — SQLite repositories

**Prompt:**
> How should I structure SQLite repositories for JournalEntry with embedded JournalLines? The entry is an aggregate with a list of lines.

**Used:** Two-step load — fetch `journal_entries` row, then fetch `journal_lines` by `entry_id`. Store `Decimal` as `REAL` in SQLite and reconstruct via `Decimal(str(float_value))` to avoid floating-point drift.

---

## 7 — Streamlit DI

**Prompt:**
> How should I wire repositories in a Streamlit multipage app where each page is a separate script? How to share a single SQLite connection?

**Used:** `@st.cache_resource` on the factory function in `app.py`, imported by each page. Cache persists for the Streamlit session lifecycle, giving one shared connection.

---

## 8 — Test structure

**Prompt:**
> What should the test suite cover for a domain like this? I want unit tests that don't touch the database.

**Used:** Three test groups:
- `test_journal.py` — aggregate invariants (balance, validation)
- `test_posting.py` — posting rules produce correct debit/credit pairs
- `test_use_cases.py` — use case orchestration via in-memory repos, including error cases and report calculations

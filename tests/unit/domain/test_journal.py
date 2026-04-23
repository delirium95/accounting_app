from datetime import date
from decimal import Decimal

import pytest

from domain.exceptions import UnbalancedEntryError
from domain.journal import DocumentType, JournalEntry, JournalLine


def _make_entry(debit: Decimal, credit: Decimal) -> JournalEntry:
    return JournalEntry(
        id=None,
        date=date(2025, 1, 1),
        description="Test entry",
        document_type=DocumentType.CUSTOMER_INVOICE,
        lines=(
            JournalLine(account_code="1100", debit=debit, credit=Decimal(0)),
            JournalLine(account_code="4000", debit=Decimal(0), credit=credit),
        ),
    )


def test_balanced_entry_is_valid() -> None:
    entry = _make_entry(Decimal("500.00"), Decimal("500.00"))
    assert entry.is_balanced


def test_unbalanced_entry_raises_on_assert() -> None:
    entry = _make_entry(Decimal("500.00"), Decimal("400.00"))
    with pytest.raises(UnbalancedEntryError):
        entry.assert_balanced()


def test_total_debit_and_credit_computed_correctly() -> None:
    entry = _make_entry(Decimal("1234.56"), Decimal("1234.56"))
    assert entry.total_debit == Decimal("1234.56")
    assert entry.total_credit == Decimal("1234.56")


def test_journal_line_rejects_negative_debit() -> None:
    with pytest.raises(Exception):
        JournalLine(account_code="1100", debit=Decimal("-1"), credit=Decimal(0))


def test_journal_line_rejects_both_debit_and_credit() -> None:
    with pytest.raises(Exception):
        JournalLine(account_code="1100", debit=Decimal("100"), credit=Decimal("50"))


def test_empty_description_raises() -> None:
    with pytest.raises(Exception):
        JournalEntry(
            id=None,
            date=date(2025, 1, 1),
            description="   ",
            document_type=DocumentType.CUSTOMER_INVOICE,
            lines=(
                JournalLine(account_code="1100", debit=Decimal("100"), credit=Decimal(0)),
                JournalLine(account_code="4000", debit=Decimal(0), credit=Decimal("100")),
            ),
        )

from datetime import date
from decimal import Decimal

from domain.accounts import ACCOUNTS_PAYABLE, ACCOUNTS_RECEIVABLE, CASH, EXPENSE, REVENUE
from domain.journal import DocumentType, JournalEntry, JournalLine

_ZERO = Decimal(0)


class PostingRules:
    """
    Domain service that encodes how business events map to journal entries.
    Every method returns a validated, balanced JournalEntry ready for persistence.
    """

    @staticmethod
    def customer_invoice(
        partner_id: int,
        amount: Decimal,
        entry_date: date,
        description: str,
    ) -> JournalEntry:
        """Dr Accounts Receivable / Cr Revenue"""
        entry = JournalEntry(
            id=None,
            date=entry_date,
            description=description,
            document_type=DocumentType.CUSTOMER_INVOICE,
            lines=(
                JournalLine(account_code=ACCOUNTS_RECEIVABLE, debit=amount, credit=_ZERO, partner_id=partner_id),
                JournalLine(account_code=REVENUE, debit=_ZERO, credit=amount, partner_id=partner_id),
            ),
        )
        entry.assert_balanced()
        return entry

    @staticmethod
    def customer_payment(
        partner_id: int,
        amount: Decimal,
        entry_date: date,
        description: str,
    ) -> JournalEntry:
        """Dr Cash / Cr Accounts Receivable"""
        entry = JournalEntry(
            id=None,
            date=entry_date,
            description=description,
            document_type=DocumentType.CUSTOMER_PAYMENT,
            lines=(
                JournalLine(account_code=CASH, debit=amount, credit=_ZERO),
                JournalLine(account_code=ACCOUNTS_RECEIVABLE, debit=_ZERO, credit=amount, partner_id=partner_id),
            ),
        )
        entry.assert_balanced()
        return entry

    @staticmethod
    def vendor_bill(
        partner_id: int,
        amount: Decimal,
        entry_date: date,
        description: str,
    ) -> JournalEntry:
        """Dr Expense / Cr Accounts Payable"""
        entry = JournalEntry(
            id=None,
            date=entry_date,
            description=description,
            document_type=DocumentType.VENDOR_BILL,
            lines=(
                JournalLine(account_code=EXPENSE, debit=amount, credit=_ZERO, partner_id=partner_id),
                JournalLine(account_code=ACCOUNTS_PAYABLE, debit=_ZERO, credit=amount, partner_id=partner_id),
            ),
        )
        entry.assert_balanced()
        return entry

    @staticmethod
    def vendor_payment(
        partner_id: int,
        amount: Decimal,
        entry_date: date,
        description: str,
    ) -> JournalEntry:
        """Dr Accounts Payable / Cr Cash"""
        entry = JournalEntry(
            id=None,
            date=entry_date,
            description=description,
            document_type=DocumentType.VENDOR_PAYMENT,
            lines=(
                JournalLine(account_code=ACCOUNTS_PAYABLE, debit=amount, credit=_ZERO, partner_id=partner_id),
                JournalLine(account_code=CASH, debit=_ZERO, credit=amount),
            ),
        )
        entry.assert_balanced()
        return entry

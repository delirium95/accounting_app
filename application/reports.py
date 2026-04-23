from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from domain.accounts import ACCOUNTS_PAYABLE, ACCOUNTS_RECEIVABLE, EXPENSE, REVENUE
from domain.interfaces import JournalRepository, PartnerRepository


@dataclass(frozen=True)
class PnLReport:
    revenue: Decimal
    expenses: Decimal

    @property
    def net_income(self) -> Decimal:
        return self.revenue - self.expenses


@dataclass(frozen=True)
class PartnerLedgerLine:
    entry_date: date
    description: str
    document_type: str
    partner_id: int
    partner_name: str
    partner_type: str
    account_code: str
    debit: Decimal
    credit: Decimal


@dataclass(frozen=True)
class PartnerBalance:
    partner_id: int
    partner_name: str
    partner_type: str
    balance: Decimal


class PnLQuery:
    def __init__(self, journal_repo: JournalRepository) -> None:
        self._journal = journal_repo

    def execute(self, date_from: date | None = None, date_to: date | None = None) -> PnLReport:
        revenue = Decimal(0)
        expenses = Decimal(0)

        for entry in self._journal.list_all():
            if date_from and entry.date < date_from:
                continue
            if date_to and entry.date > date_to:
                continue
            for line in entry.lines:
                if line.account_code == REVENUE:
                    revenue += line.credit - line.debit
                elif line.account_code == EXPENSE:
                    expenses += line.debit - line.credit

        return PnLReport(revenue=revenue, expenses=expenses)


class PartnerLedgerQuery:
    def __init__(self, journal_repo: JournalRepository, partner_repo: PartnerRepository) -> None:
        self._journal = journal_repo
        self._partners = partner_repo

    def lines(
        self,
        partner_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[PartnerLedgerLine]:
        partner_map = {p.id: p for p in self._partners.list_all()}
        result: list[PartnerLedgerLine] = []

        for entry in self._journal.list_all():
            if date_from and entry.date < date_from:
                continue
            if date_to and entry.date > date_to:
                continue
            for line in entry.lines:
                if line.partner_id is None:
                    continue
                if line.account_code not in (ACCOUNTS_RECEIVABLE, ACCOUNTS_PAYABLE):
                    continue
                if partner_id is not None and line.partner_id != partner_id:
                    continue
                partner = partner_map.get(line.partner_id)
                if partner is None:
                    continue
                result.append(
                    PartnerLedgerLine(
                        entry_date=entry.date,
                        description=entry.description,
                        document_type=entry.document_type.value,
                        partner_id=line.partner_id,
                        partner_name=partner.name,
                        partner_type=partner.type.value,
                        account_code=line.account_code,
                        debit=line.debit,
                        credit=line.credit,
                    )
                )

        return sorted(result, key=lambda x: (x.partner_id, x.entry_date))

    def balances(self) -> list[PartnerBalance]:
        totals: dict[int, Decimal] = {}
        for p in self._partners.list_all():
            totals[p.id] = Decimal(0)

        for line in self.lines():
            if line.account_code == ACCOUNTS_RECEIVABLE:
                # AR: debit = invoice (customer owes us), credit = payment received
                totals[line.partner_id] += line.debit - line.credit
            elif line.account_code == ACCOUNTS_PAYABLE:
                # AP: credit = bill (we owe vendor), debit = payment made
                totals[line.partner_id] += line.credit - line.debit

        partner_map = {p.id: p for p in self._partners.list_all()}
        return [
            PartnerBalance(
                partner_id=pid,
                partner_name=partner_map[pid].name,
                partner_type=partner_map[pid].type.value,
                balance=balance,
            )
            for pid, balance in totals.items()
            if pid in partner_map
        ]

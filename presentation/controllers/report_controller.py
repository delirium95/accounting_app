from datetime import date

from application.reports import PartnerBalance, PartnerLedgerLine, PartnerLedgerQuery, PnLQuery, PnLReport
from domain.interfaces import JournalRepository, PartnerRepository
from presentation.base import BaseController


class ReportController(BaseController):
    def __init__(self, journal_repo: JournalRepository, partner_repo: PartnerRepository) -> None:
        super().__init__(journal_repo, partner_repo)
        self._pnl_query = PnLQuery(journal_repo)
        self._ledger_query = PartnerLedgerQuery(journal_repo, partner_repo)

    def pnl(self, date_from: date | None = None, date_to: date | None = None) -> PnLReport:
        return self._pnl_query.execute(date_from=date_from, date_to=date_to)

    def partner_balances(self) -> list[PartnerBalance]:
        return self._ledger_query.balances()

    def ledger_lines(self, date_from: date | None = None, date_to: date | None = None) -> list[PartnerLedgerLine]:
        return self._ledger_query.lines(date_from=date_from, date_to=date_to)

from app import get_repos
from presentation.controllers.partner_controller import PartnerController
from presentation.controllers.transaction_controller import TransactionController
from presentation.views.bill_view import BillView

journal_repo, partner_repo = get_repos()
BillView(
    transaction_ctrl=TransactionController(journal_repo=journal_repo, partner_repo=partner_repo),
    partner_ctrl=PartnerController(partner_repo=partner_repo),
).render()

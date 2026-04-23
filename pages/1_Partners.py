from app import get_repos
from presentation.controllers.partner_controller import PartnerController
from presentation.views.partner_view import PartnerView

journal_repo, partner_repo = get_repos()
PartnerView(controller=PartnerController(partner_repo=partner_repo)).render()

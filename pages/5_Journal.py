from app import get_repos
from presentation.controllers.journal_controller import JournalController
from presentation.views.journal_view import JournalView

journal_repo, partner_repo = get_repos()
JournalView(controller=JournalController(journal_repo=journal_repo, partner_repo=partner_repo)).render()

from app import get_repos
from presentation.controllers.report_controller import ReportController
from presentation.views.report_view import ReportView

journal_repo, partner_repo = get_repos()
ReportView(controller=ReportController(journal_repo=journal_repo, partner_repo=partner_repo)).render()

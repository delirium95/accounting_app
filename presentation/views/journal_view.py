import streamlit as st

from presentation.base import BaseView
from presentation.controllers.journal_controller import JournalController
from presentation.views.shared import render_journal_entry


class JournalView(BaseView):
    def __init__(self, controller: JournalController) -> None:
        self._ctrl = controller

    def render(self) -> None:
        st.title("Journal")
        st.caption("All posted accounting entries")

        entries = self._ctrl.list_entries()
        if not entries:
            st.info("No journal entries yet.")
            return

        partner_map = self._ctrl.partner_map()
        for entry in entries:
            render_journal_entry(entry=entry, partner_map=partner_map)

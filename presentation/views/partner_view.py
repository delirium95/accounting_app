import pandas as pd
import streamlit as st
from pydantic import ValidationError

from presentation.base import BaseView
from presentation.controllers.partner_controller import PartnerController


class PartnerView(BaseView):
    def __init__(self, controller: PartnerController) -> None:
        self._ctrl = controller

    def render(self) -> None:
        st.title("Partners")
        self._render_form()
        st.divider()
        self._render_list()

    def _render_form(self) -> None:
        with st.form("add_partner", clear_on_submit=True):
            st.subheader("Add Partner")
            name = st.text_input("Name")
            partner_type = st.selectbox("Type", ["customer", "vendor"])
            if st.form_submit_button("Add"):
                try:
                    partner = self._ctrl.add(name=name, partner_type=partner_type)
                    st.success(f"Partner '{partner.name}' added.")
                    st.rerun()
                except (ValidationError, ValueError) as exc:
                    st.error(str(exc))

    def _render_list(self) -> None:
        st.subheader("All Partners")
        partners = self._ctrl.list_all()
        if partners:
            df = pd.DataFrame([{"ID": p.id, "Name": p.name, "Type": p.type.value} for p in partners])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No partners yet.")

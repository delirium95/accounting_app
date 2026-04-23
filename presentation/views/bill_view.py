from decimal import Decimal

import pandas as pd
import streamlit as st

from domain.partner import Partner
from presentation.base import BaseView
from presentation.controllers.partner_controller import PartnerController
from presentation.controllers.transaction_controller import TransactionController
from presentation.views.shared import render_amount_input, render_date_input, render_description_input


class BillView(BaseView):
    def __init__(self, transaction_ctrl: TransactionController, partner_ctrl: PartnerController) -> None:
        self._tx = transaction_ctrl
        self._partners = partner_ctrl

    def render(self) -> None:
        st.title("Vendor Bills")
        st.caption("Dr Expense (5000) / Cr Accounts Payable (2000)")

        vendors = self._partners.list_vendors()
        if not vendors:
            st.warning("No vendors found. Add a vendor in the Partners page first.")
            return

        self._render_form(vendors)
        st.divider()
        self._render_list()

    def _render_form(self, vendors: list[Partner]) -> None:
        with st.form("bill_form", clear_on_submit=True):
            vendor = st.selectbox("Vendor", vendors, format_func=lambda p: p.name)
            amount = render_amount_input()
            entry_date = render_date_input()
            description = render_description_input()
            if st.form_submit_button("Post Bill"):
                if not description.strip():
                    st.error("Description is required.")
                    return
                entry = self._tx.post_bill(
                    partner_id=vendor.id,
                    amount=Decimal(str(amount)),
                    entry_date=entry_date,
                    description=description,
                )
                st.success(f"Bill posted (entry #{entry.id}) — Dr Expense ${amount:,.2f} / Cr AP ${amount:,.2f}")
                st.rerun()

    def _render_list(self) -> None:
        st.subheader("Posted Bills")
        bills = self._tx.list_bills()
        if not bills:
            st.info("No bills posted yet.")
            return

        partner_map = {p.id: p.name for p in self._partners.list_all()}
        rows = []
        for entry in bills:
            exp_line = next((l for l in entry.lines if l.account_code == "5000"), None)
            rows.append({
                "Date": str(entry.date),
                "Vendor": partner_map.get(exp_line.partner_id, "—") if exp_line else "—",
                "Amount": f"${exp_line.debit:,.2f}" if exp_line else "—",
                "Description": entry.description,
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

from decimal import Decimal

import pandas as pd
import streamlit as st

from domain.partner import Partner
from presentation.base import BaseView
from presentation.controllers.partner_controller import PartnerController
from presentation.controllers.transaction_controller import TransactionController
from presentation.views.shared import render_amount_input, render_date_input, render_description_input


class InvoiceView(BaseView):
    def __init__(self, transaction_ctrl: TransactionController, partner_ctrl: PartnerController) -> None:
        self._tx = transaction_ctrl
        self._partners = partner_ctrl

    def render(self) -> None:
        st.title("Customer Invoices")
        st.caption("Dr Accounts Receivable (1100) / Cr Revenue (4000)")

        customers = self._partners.list_customers()
        if not customers:
            st.warning("No customers found. Add a customer in the Partners page first.")
            return

        self._render_form(customers)
        st.divider()
        self._render_list()

    def _render_form(self, customers: list[Partner]) -> None:
        with st.form("invoice_form", clear_on_submit=True):
            customer = st.selectbox("Customer", customers, format_func=lambda p: p.name)
            amount = render_amount_input()
            entry_date = render_date_input()
            description = render_description_input()
            if st.form_submit_button("Post Invoice"):
                if not description.strip():
                    st.error("Description is required.")
                    return
                entry = self._tx.post_invoice(
                    partner_id=customer.id,
                    amount=Decimal(str(amount)),
                    entry_date=entry_date,
                    description=description,
                )
                st.success(f"Invoice posted (entry #{entry.id}) — Dr AR ${amount:,.2f} / Cr Revenue ${amount:,.2f}")
                st.rerun()

    def _render_list(self) -> None:
        st.subheader("Posted Invoices")
        invoices = self._tx.list_invoices()
        if not invoices:
            st.info("No invoices posted yet.")
            return

        partner_map = {p.id: p.name for p in self._partners.list_all()}
        rows = []
        for entry in invoices:
            ar_line = next((l for l in entry.lines if l.account_code == "1100"), None)
            rows.append({
                "Date": str(entry.date),
                "Customer": partner_map.get(ar_line.partner_id, "—") if ar_line else "—",
                "Amount": f"${ar_line.debit:,.2f}" if ar_line else "—",
                "Description": entry.description,
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

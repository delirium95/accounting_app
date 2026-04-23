from collections.abc import Callable
from datetime import date
from decimal import Decimal

import streamlit as st

from domain.exceptions import DomainError
from domain.journal import JournalEntry
from domain.partner import Partner
from presentation.base import BaseView
from presentation.controllers.partner_controller import PartnerController
from presentation.controllers.transaction_controller import TransactionController
from presentation.views.shared import render_amount_input, render_date_input, render_description_input

type PaymentHandler = Callable[[int, Decimal, date, str], JournalEntry]


class PaymentView(BaseView):
    def __init__(self, transaction_ctrl: TransactionController, partner_ctrl: PartnerController) -> None:
        self._tx = transaction_ctrl
        self._partners = partner_ctrl

    def render(self) -> None:
        st.title("Payments")
        tab_customer, tab_vendor = st.tabs(["Customer Payment", "Vendor Payment"])

        with tab_customer:
            self._render_customer_payment()

        with tab_vendor:
            self._render_vendor_payment()

    def _render_customer_payment(self) -> None:
        st.caption("Dr Cash (1000) / Cr Accounts Receivable (1100)")
        customers = self._partners.list_customers()
        if not customers:
            st.warning("No customers found.")
            return
        self._render_payment_form(
            partners=customers,
            form_key="customer_pmt_form",
            input_key_suffix="cp",
            submit_label="Post Customer Payment",
            on_submit=self._tx.post_customer_payment,
            success_msg_template="Dr Cash ${amount:,.2f} / Cr AR ${amount:,.2f}",
        )

    def _render_vendor_payment(self) -> None:
        st.caption("Dr Accounts Payable (2000) / Cr Cash (1000)")
        vendors = self._partners.list_vendors()
        if not vendors:
            st.warning("No vendors found.")
            return
        self._render_payment_form(
            partners=vendors,
            form_key="vendor_pmt_form",
            input_key_suffix="vp",
            submit_label="Post Vendor Payment",
            on_submit=self._tx.post_vendor_payment,
            success_msg_template="Dr AP ${amount:,.2f} / Cr Cash ${amount:,.2f}",
        )

    def _render_payment_form(
        self,
        partners: list[Partner],
        form_key: str,
        input_key_suffix: str,
        submit_label: str,
        on_submit: PaymentHandler,
        success_msg_template: str,
    ) -> None:
        with st.form(form_key, clear_on_submit=True):
            partner = st.selectbox("Partner", partners, format_func=lambda p: p.name)
            amount = render_amount_input(key=f"{input_key_suffix}_amt")
            entry_date = render_date_input(key=f"{input_key_suffix}_date")
            description = render_description_input(key=f"{input_key_suffix}_desc")
            if st.form_submit_button(submit_label):
                if not description.strip():
                    st.error("Description is required.")
                    return
                try:
                    entry = on_submit(
                        partner_id=partner.id,
                        amount=Decimal(str(amount)),
                        entry_date=entry_date,
                        description=description,
                    )
                    st.success(f"Payment posted (entry #{entry.id}) — {success_msg_template.format(amount=amount)}")
                    st.rerun()
                except DomainError as exc:
                    st.error(str(exc))

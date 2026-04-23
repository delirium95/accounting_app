from datetime import date
from decimal import Decimal

import streamlit as st

from application.commands import PostCustomerPaymentCommand, PostVendorPaymentCommand
from application.use_cases import PostCustomerPayment, PostVendorPayment
from app import get_repos
from domain.partner import PartnerType

st.title("Payments")

journal_repo, partner_repo = get_repos()

tab_customer, tab_vendor = st.tabs(["Customer Payment", "Vendor Payment"])

with tab_customer:
    st.caption("Dr Cash (1000) / Cr Accounts Receivable (1100)")
    customers = partner_repo.list_by_type(PartnerType.CUSTOMER)
    if not customers:
        st.warning("No customers found.")
    else:
        with st.form("customer_pmt_form", clear_on_submit=True):
            customer = st.selectbox("Customer", customers, format_func=lambda p: p.name)
            amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f", key="cp_amt")
            entry_date = st.date_input("Date", value=date.today(), key="cp_date")
            description = st.text_input("Description", key="cp_desc")
            if st.form_submit_button("Post Payment"):
                if description.strip():
                    entry = PostCustomerPayment(journal_repo, partner_repo).execute(
                        PostCustomerPaymentCommand(
                            partner_id=customer.id,
                            amount=Decimal(str(amount)),
                            date=entry_date,
                            description=description,
                        )
                    )
                    st.success(f"Payment posted (entry #{entry.id}) — Dr Cash ${amount:,.2f} / Cr AR ${amount:,.2f}")
                    st.rerun()
                else:
                    st.error("Description is required.")

with tab_vendor:
    st.caption("Dr Accounts Payable (2000) / Cr Cash (1000)")
    vendors = partner_repo.list_by_type(PartnerType.VENDOR)
    if not vendors:
        st.warning("No vendors found.")
    else:
        with st.form("vendor_pmt_form", clear_on_submit=True):
            vendor = st.selectbox("Vendor", vendors, format_func=lambda p: p.name)
            amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f", key="vp_amt")
            entry_date = st.date_input("Date", value=date.today(), key="vp_date")
            description = st.text_input("Description", key="vp_desc")
            if st.form_submit_button("Post Payment"):
                if description.strip():
                    entry = PostVendorPayment(journal_repo, partner_repo).execute(
                        PostVendorPaymentCommand(
                            partner_id=vendor.id,
                            amount=Decimal(str(amount)),
                            date=entry_date,
                            description=description,
                        )
                    )
                    st.success(f"Payment posted (entry #{entry.id}) — Dr AP ${amount:,.2f} / Cr Cash ${amount:,.2f}")
                    st.rerun()
                else:
                    st.error("Description is required.")

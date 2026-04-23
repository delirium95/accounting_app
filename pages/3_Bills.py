from datetime import date
from decimal import Decimal

import streamlit as st

from application.commands import PostBillCommand
from application.use_cases import PostVendorBill
from app import get_repos
from domain.journal import DocumentType
from domain.partner import PartnerType

st.title("Vendor Bills")
st.caption("Dr Expense (5000) / Cr Accounts Payable (2000)")

journal_repo, partner_repo = get_repos()
vendors = partner_repo.list_by_type(PartnerType.VENDOR)

if not vendors:
    st.warning("No vendors found. Add a vendor in the Partners page first.")
else:
    with st.form("bill_form", clear_on_submit=True):
        vendor = st.selectbox("Vendor", vendors, format_func=lambda p: p.name)
        amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")
        entry_date = st.date_input("Date", value=date.today())
        description = st.text_input("Description")
        if st.form_submit_button("Post Bill"):
            if description.strip():
                entry = PostVendorBill(journal_repo, partner_repo).execute(
                    PostBillCommand(
                        partner_id=vendor.id,
                        amount=Decimal(str(amount)),
                        date=entry_date,
                        description=description,
                    )
                )
                st.success(f"Bill posted (entry #{entry.id}) — Dr Expense ${amount:,.2f} / Cr AP ${amount:,.2f}")
                st.rerun()
            else:
                st.error("Description is required.")

st.divider()
st.subheader("Posted Bills")

import pandas as pd

bills = [e for e in journal_repo.list_all() if e.document_type == DocumentType.VENDOR_BILL]
if bills:
    partner_map = {p.id: p.name for p in partner_repo.list_all()}
    rows = []
    for e in bills:
        exp_line = next((l for l in e.lines if l.account_code == "5000"), None)
        rows.append({
            "Date": str(e.date),
            "Vendor": partner_map.get(exp_line.partner_id, "—") if exp_line else "—",
            "Amount": f"${exp_line.debit:,.2f}" if exp_line else "—",
            "Description": e.description,
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("No bills posted yet.")

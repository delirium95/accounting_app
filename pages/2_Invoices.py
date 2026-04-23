from datetime import date
from decimal import Decimal

import streamlit as st

from application.commands import PostInvoiceCommand
from application.use_cases import PostCustomerInvoice
from app import get_repos

st.title("Customer Invoices")
st.caption("Dr Accounts Receivable (1100) / Cr Revenue (4000)")

journal_repo, partner_repo = get_repos()
customers = partner_repo.list_by_type(__import__("domain.partner", fromlist=["PartnerType"]).PartnerType.CUSTOMER)

if not customers:
    st.warning("No customers found. Add a customer in the Partners page first.")
else:
    with st.form("invoice_form", clear_on_submit=True):
        customer = st.selectbox("Customer", customers, format_func=lambda p: p.name)
        amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")
        entry_date = st.date_input("Date", value=date.today())
        description = st.text_input("Description")
        if st.form_submit_button("Post Invoice"):
            if description.strip():
                entry = PostCustomerInvoice(journal_repo, partner_repo).execute(
                    PostInvoiceCommand(
                        partner_id=customer.id,
                        amount=Decimal(str(amount)),
                        date=entry_date,
                        description=description,
                    )
                )
                st.success(f"Invoice posted (entry #{entry.id}) — Dr AR ${amount:,.2f} / Cr Revenue ${amount:,.2f}")
                st.rerun()
            else:
                st.error("Description is required.")

st.divider()
st.subheader("Posted Invoices")

import pandas as pd
from domain.journal import DocumentType

invoices = [e for e in journal_repo.list_all() if e.document_type == DocumentType.CUSTOMER_INVOICE]
if invoices:
    partner_map = {p.id: p.name for p in partner_repo.list_all()}
    rows = []
    for e in invoices:
        ar_line = next((l for l in e.lines if l.account_code == "1100"), None)
        rows.append({
            "Date": str(e.date),
            "Customer": partner_map.get(ar_line.partner_id, "—") if ar_line else "—",
            "Amount": f"${ar_line.debit:,.2f}" if ar_line else "—",
            "Description": e.description,
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("No invoices posted yet.")

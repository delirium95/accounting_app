from datetime import date

import pandas as pd
import streamlit as st

from app import get_repos
from application.reports import PartnerLedgerQuery, PnLQuery

st.title("Reports")

journal_repo, partner_repo = get_repos()

tab_pnl, tab_ledger = st.tabs(["Profit & Loss", "Partner Ledger"])

with tab_pnl:
    st.subheader("Profit & Loss")
    col1, col2 = st.columns(2)
    date_from = col1.date_input("From", value=date.today().replace(day=1))
    date_to = col2.date_input("To", value=date.today())

    report = PnLQuery(journal_repo).execute(date_from=date_from, date_to=date_to)

    m1, m2, m3 = st.columns(3)
    m1.metric("Revenue", f"${report.revenue:,.2f}")
    m2.metric("Expenses", f"${report.expenses:,.2f}")
    m3.metric("Net Income", f"${report.net_income:,.2f}")

    st.divider()
    pnl_df = pd.DataFrame([
        {"Line": "Revenue (4000)", "Amount": f"${report.revenue:,.2f}"},
        {"Line": "Expenses (5000)", "Amount": f"(${report.expenses:,.2f})"},
        {"Line": "Net Income", "Amount": f"${report.net_income:,.2f}"},
    ])
    st.dataframe(pnl_df, use_container_width=True, hide_index=True)

with tab_ledger:
    st.subheader("Partner Ledger")
    query = PartnerLedgerQuery(journal_repo, partner_repo)

    st.caption("Current outstanding balances")
    balances = query.balances()
    if balances:
        bal_df = pd.DataFrame([
            {"Partner": b.partner_name, "Type": b.partner_type, "Outstanding": f"${b.balance:,.2f}"}
            for b in balances
        ])
        st.dataframe(bal_df, use_container_width=True, hide_index=True)
    else:
        st.info("No partner movements yet.")

    st.divider()
    st.caption("Movements")
    col1, col2 = st.columns(2)
    date_from_l = col1.date_input("From", value=date.today().replace(day=1), key="l_from")
    date_to_l = col2.date_input("To", value=date.today(), key="l_to")

    lines = query.lines(date_from=date_from_l, date_to=date_to_l)
    if lines:
        lines_df = pd.DataFrame([
            {
                "Date": str(ln.entry_date),
                "Partner": ln.partner_name,
                "Type": ln.partner_type,
                "Account": ln.account_code,
                "Document": ln.document_type,
                "Description": ln.description,
                "Debit": f"${ln.debit:,.2f}" if ln.debit else "",
                "Credit": f"${ln.credit:,.2f}" if ln.credit else "",
            }
            for ln in lines
        ])
        st.dataframe(lines_df, use_container_width=True, hide_index=True)
    else:
        st.info("No movements in this period.")

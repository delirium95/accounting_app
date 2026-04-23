import streamlit as st

from application.reports import PartnerLedgerQuery, PnLQuery
from infrastructure.database import get_connection, init_schema
from infrastructure.repositories import SQLiteJournalRepository, SQLitePartnerRepository
from presentation.views.shared import render_chart_of_accounts, render_partner_balance_table

st.set_page_config(page_title="Accounting App", page_icon="📒", layout="wide")


@st.cache_resource
def get_repos() -> tuple[SQLiteJournalRepository, SQLitePartnerRepository]:
    conn = get_connection()
    init_schema(conn)
    return SQLiteJournalRepository(conn), SQLitePartnerRepository(conn)


def main() -> None:
    journal_repo, partner_repo = get_repos()

    st.title("📒 Accounting App")
    st.caption("Minimal double-entry bookkeeping")

    pnl = PnLQuery(journal_repo).execute()
    col1, col2, col3 = st.columns(3)
    col1.metric("Revenue", f"${pnl.revenue:,.2f}")
    col2.metric("Expenses", f"${pnl.expenses:,.2f}")
    col3.metric("Net Income", f"${pnl.net_income:,.2f}")

    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("Partner Balances")
        render_partner_balance_table(PartnerLedgerQuery(journal_repo, partner_repo).balances())

    with right:
        st.subheader("Chart of Accounts")
        render_chart_of_accounts()


main()

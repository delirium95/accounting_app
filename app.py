import streamlit as st

from application.reports import PartnerLedgerQuery, PnLQuery
from infrastructure.database import get_connection, init_schema
from infrastructure.repositories import SQLiteJournalRepository, SQLitePartnerRepository

st.set_page_config(page_title="Accounting App", page_icon="📒", layout="wide")


@st.cache_resource
def get_repos():
    conn = get_connection()
    init_schema(conn)
    partner_repo = SQLitePartnerRepository(conn)
    journal_repo = SQLiteJournalRepository(conn)
    return journal_repo, partner_repo


journal_repo, partner_repo = get_repos()

st.title("📒 Accounting App")
st.caption("Minimal double-entry bookkeeping")

pnl = PnLQuery(journal_repo).execute()
balances = PartnerLedgerQuery(journal_repo, partner_repo).balances()

col1, col2, col3 = st.columns(3)
col1.metric("Revenue", f"${pnl.revenue:,.2f}")
col2.metric("Expenses", f"${pnl.expenses:,.2f}")
col3.metric("Net Income", f"${pnl.net_income:,.2f}")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Partner Balances")
    if balances:
        import pandas as pd
        df = pd.DataFrame([
            {"Partner": b.partner_name, "Type": b.partner_type, "Outstanding": f"${b.balance:,.2f}"}
            for b in balances
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No partners yet.")

with right:
    st.subheader("Chart of Accounts")
    from domain.accounts import CHART_OF_ACCOUNTS
    import pandas as pd
    coa = pd.DataFrame([
        {"Code": a.code, "Name": a.name, "Type": a.type.value, "Normal": a.normal_balance.value}
        for a in CHART_OF_ACCOUNTS.values()
    ])
    st.dataframe(coa, use_container_width=True, hide_index=True)

import pandas as pd
import streamlit as st

from app import get_repos
from domain.accounts import CHART_OF_ACCOUNTS

st.title("Journal")
st.caption("All posted accounting entries")

journal_repo, partner_repo = get_repos()
partner_map = {p.id: p.name for p in partner_repo.list_all()}
entries = journal_repo.list_all()

if not entries:
    st.info("No journal entries yet.")
else:
    for entry in entries:
        label = f"#{entry.id} — {entry.date} — {entry.description} [{entry.document_type.value}]"
        with st.expander(label):
            rows = []
            for line in entry.lines:
                account = CHART_OF_ACCOUNTS.get(line.account_code)
                rows.append({
                    "Account": f"{line.account_code} {account.name if account else ''}",
                    "Debit": f"${line.debit:,.2f}" if line.debit else "",
                    "Credit": f"${line.credit:,.2f}" if line.credit else "",
                    "Partner": partner_map.get(line.partner_id, "") if line.partner_id else "",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

import streamlit as st

from application.commands import AddPartnerCommand
from application.use_cases import AddPartner
from app import get_repos

st.title("Partners")

journal_repo, partner_repo = get_repos()

with st.form("add_partner", clear_on_submit=True):
    st.subheader("Add Partner")
    name = st.text_input("Name")
    partner_type = st.selectbox("Type", ["customer", "vendor"])
    if st.form_submit_button("Add"):
        if name.strip():
            AddPartner(partner_repo).execute(AddPartnerCommand(name=name, partner_type=partner_type))
            st.success(f"Partner '{name}' added.")
            st.rerun()
        else:
            st.error("Name is required.")

st.divider()
st.subheader("All Partners")

partners = partner_repo.list_all()
if partners:
    import pandas as pd
    df = pd.DataFrame([{"ID": p.id, "Name": p.name, "Type": p.type.value} for p in partners])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No partners yet.")

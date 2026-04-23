"""Reusable Streamlit rendering helpers shared across views."""
from datetime import date

import pandas as pd
import streamlit as st

from application.reports import PartnerBalance, PartnerLedgerLine
from domain.accounts import CHART_OF_ACCOUNTS
from domain.journal import JournalEntry
from domain.partner import Partner


def render_partner_selector(partners: list[Partner], label: str = "Partner") -> Partner | None:
    if not partners:
        return None
    return st.selectbox(label, partners, format_func=lambda p: p.name)


def render_amount_input(key: str = "amount") -> float:
    return st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f", key=key)


def render_date_input(label: str = "Date", key: str = "date") -> date:
    return st.date_input(label, value=date.today(), key=key)


def render_description_input(key: str = "description") -> str:
    return st.text_input("Description", key=key)


def render_partner_balance_table(balances: list[PartnerBalance]) -> None:
    if balances:
        df = pd.DataFrame([
            {"Partner": b.partner_name, "Type": b.partner_type, "Outstanding": f"${b.balance:,.2f}"}
            for b in balances
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No partner movements yet.")


def render_ledger_lines_table(lines: list[PartnerLedgerLine]) -> None:
    if lines:
        df = pd.DataFrame([
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
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No movements in this period.")


def render_journal_entry(entry: JournalEntry, partner_map: dict[int, str]) -> None:
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


def render_chart_of_accounts() -> None:
    df = pd.DataFrame([
        {"Code": a.code, "Name": a.name, "Type": a.type.value, "Normal": a.normal_balance.value}
        for a in CHART_OF_ACCOUNTS.values()
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

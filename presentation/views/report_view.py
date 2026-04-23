from datetime import date

import pandas as pd
import streamlit as st

from application.reports import PnLReport
from presentation.base import BaseView
from presentation.controllers.report_controller import ReportController
from presentation.views.shared import render_ledger_lines_table, render_partner_balance_table


class ReportView(BaseView):
    def __init__(self, controller: ReportController) -> None:
        self._ctrl = controller

    def render(self) -> None:
        st.title("Reports")
        tab_pnl, tab_ledger = st.tabs(["Profit & Loss", "Partner Ledger"])

        with tab_pnl:
            self._render_pnl()

        with tab_ledger:
            self._render_ledger()

    def _render_pnl(self) -> None:
        st.subheader("Profit & Loss")
        col1, col2 = st.columns(2)
        date_from = col1.date_input("From", value=date.today().replace(day=1))
        date_to = col2.date_input("To", value=date.today())

        report = self._ctrl.pnl(date_from=date_from, date_to=date_to)
        self._render_pnl_metrics(report)
        st.divider()
        self._render_pnl_table(report)

    def _render_pnl_metrics(self, report: PnLReport) -> None:
        m1, m2, m3 = st.columns(3)
        m1.metric("Revenue", f"${report.revenue:,.2f}")
        m2.metric("Expenses", f"${report.expenses:,.2f}")
        m3.metric("Net Income", f"${report.net_income:,.2f}")

    def _render_pnl_table(self, report: PnLReport) -> None:
        df = pd.DataFrame([
            {"Line": "Revenue (4000)", "Amount": f"${report.revenue:,.2f}"},
            {"Line": "Expenses (5000)", "Amount": f"(${report.expenses:,.2f})"},
            {"Line": "Net Income", "Amount": f"${report.net_income:,.2f}"},
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

    def _render_ledger(self) -> None:
        st.subheader("Partner Ledger")
        st.caption("Current outstanding balances")
        render_partner_balance_table(self._ctrl.partner_balances())

        st.divider()
        st.caption("Movements")
        col1, col2 = st.columns(2)
        date_from = col1.date_input("From", value=date.today().replace(day=1), key="l_from")
        date_to = col2.date_input("To", value=date.today(), key="l_to")
        render_ledger_lines_table(self._ctrl.ledger_lines(date_from=date_from, date_to=date_to))

from dataclasses import dataclass
from enum import Enum


class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    REVENUE = "revenue"
    EXPENSE = "expense"


class NormalBalance(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


@dataclass(frozen=True)
class Account:
    code: str
    name: str
    type: AccountType
    normal_balance: NormalBalance


CHART_OF_ACCOUNTS: dict[str, Account] = {
    "1000": Account("1000", "Cash", AccountType.ASSET, NormalBalance.DEBIT),
    "1100": Account("1100", "Accounts Receivable", AccountType.ASSET, NormalBalance.DEBIT),
    "2000": Account("2000", "Accounts Payable", AccountType.LIABILITY, NormalBalance.CREDIT),
    "4000": Account("4000", "Revenue", AccountType.REVENUE, NormalBalance.CREDIT),
    "5000": Account("5000", "Expense", AccountType.EXPENSE, NormalBalance.DEBIT),
}

CASH = "1000"
ACCOUNTS_RECEIVABLE = "1100"
ACCOUNTS_PAYABLE = "2000"
REVENUE = "4000"
EXPENSE = "5000"

from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class DocumentType(str, Enum):
    CUSTOMER_INVOICE = "customer_invoice"
    CUSTOMER_PAYMENT = "customer_payment"
    VENDOR_BILL = "vendor_bill"
    VENDOR_PAYMENT = "vendor_payment"


class JournalLine(BaseModel):
    """Value object — one side of a double-entry posting."""

    model_config = ConfigDict(frozen=True)

    account_code: str
    debit: Decimal
    credit: Decimal
    partner_id: int | None = None

    @model_validator(mode="after")
    def validate_amounts(self) -> "JournalLine":
        if self.debit < 0 or self.credit < 0:
            raise ValueError("Debit and credit amounts must be non-negative")
        if self.debit > 0 and self.credit > 0:
            raise ValueError("A journal line cannot carry both debit and credit")
        return self


class JournalEntry(BaseModel):
    """Aggregate root — always validated to be balanced before persistence."""

    model_config = ConfigDict(frozen=True)

    id: int | None
    date: date
    description: str
    document_type: DocumentType
    lines: tuple[JournalLine, ...]

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()

    @property
    def total_debit(self) -> Decimal:
        return sum((line.debit for line in self.lines), Decimal(0))

    @property
    def total_credit(self) -> Decimal:
        return sum((line.credit for line in self.lines), Decimal(0))

    @property
    def is_balanced(self) -> bool:
        return self.total_debit == self.total_credit

    def assert_balanced(self) -> None:
        if not self.is_balanced:
            raise ValueError(
                f"Journal entry is not balanced: "
                f"debit={self.total_debit}, credit={self.total_credit}"
            )

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class AddPartnerCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    partner_type: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Partner name cannot be empty")
        return v.strip()

    @field_validator("partner_type")
    @classmethod
    def valid_type(cls, v: str) -> str:
        if v not in ("customer", "vendor"):
            raise ValueError("partner_type must be 'customer' or 'vendor'")
        return v


class PostInvoiceCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    partner_id: int
    amount: Decimal
    date: date
    description: str

    @field_validator("amount")
    @classmethod
    def positive_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class PostBillCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    partner_id: int
    amount: Decimal
    date: date
    description: str

    @field_validator("amount")
    @classmethod
    def positive_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class PostCustomerPaymentCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    partner_id: int
    amount: Decimal
    date: date
    description: str

    @field_validator("amount")
    @classmethod
    def positive_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class PostVendorPaymentCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    partner_id: int
    amount: Decimal
    date: date
    description: str

    @field_validator("amount")
    @classmethod
    def positive_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

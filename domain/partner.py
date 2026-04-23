from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator


class PartnerType(str, Enum):
    CUSTOMER = "customer"
    VENDOR = "vendor"


class Partner(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int | None
    name: str
    type: PartnerType

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Partner name cannot be empty")
        return v.strip()

    @property
    def is_customer(self) -> bool:
        return self.type == PartnerType.CUSTOMER

    @property
    def is_vendor(self) -> bool:
        return self.type == PartnerType.VENDOR

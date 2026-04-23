class DomainError(Exception):
    """Base for all domain-level errors."""


class PartnerNotFoundError(DomainError):
    def __init__(self, partner_id: int) -> None:
        super().__init__(f"Partner {partner_id} not found")
        self.partner_id = partner_id


class InvalidPartnerTypeError(DomainError):
    def __init__(self, expected: str, actual: str) -> None:
        super().__init__(f"Expected partner type '{expected}', got '{actual}'")
        self.expected = expected
        self.actual = actual


class UnbalancedEntryError(DomainError):
    def __init__(self, debit: object, credit: object) -> None:
        super().__init__(f"Journal entry is not balanced: debit={debit}, credit={credit}")

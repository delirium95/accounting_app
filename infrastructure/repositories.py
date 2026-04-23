import sqlite3
from datetime import date
from decimal import Decimal

from domain.interfaces import JournalRepository, PartnerRepository
from domain.journal import DocumentType, JournalEntry, JournalLine
from domain.partner import Partner, PartnerType
from infrastructure.database import transaction


class SQLitePartnerRepository(PartnerRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, partner: Partner) -> Partner:
        with transaction(self._conn) as conn:
            cur = conn.execute(
                "INSERT INTO partners (name, type) VALUES (?, ?)",
                (partner.name, partner.type.value),
            )
        return partner.model_copy(update={"id": cur.lastrowid})

    def get_by_id(self, partner_id: int) -> Partner | None:
        row = self._conn.execute(
            "SELECT id, name, type FROM partners WHERE id = ?", (partner_id,)
        ).fetchone()
        return self._row_to_partner(row) if row else None

    def list_all(self) -> list[Partner]:
        rows = self._conn.execute("SELECT id, name, type FROM partners ORDER BY name").fetchall()
        return [self._row_to_partner(r) for r in rows]

    def list_by_type(self, partner_type: PartnerType) -> list[Partner]:
        rows = self._conn.execute(
            "SELECT id, name, type FROM partners WHERE type = ? ORDER BY name",
            (partner_type.value,),
        ).fetchall()
        return [self._row_to_partner(r) for r in rows]

    @staticmethod
    def _row_to_partner(row: sqlite3.Row) -> Partner:
        return Partner(id=row["id"], name=row["name"], type=PartnerType(row["type"]))


class SQLiteJournalRepository(JournalRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, entry: JournalEntry) -> JournalEntry:
        with transaction(self._conn) as conn:
            cur = conn.execute(
                "INSERT INTO journal_entries (date, description, document_type) VALUES (?, ?, ?)",
                (str(entry.date), entry.description, entry.document_type.value),
            )
            entry_id: int = cur.lastrowid  # type: ignore[assignment]
            for line in entry.lines:
                conn.execute(
                    "INSERT INTO journal_lines (entry_id, account_code, debit, credit, partner_id) VALUES (?, ?, ?, ?, ?)",
                    (entry_id, line.account_code, float(line.debit), float(line.credit), line.partner_id),
                )
        return entry.model_copy(update={"id": entry_id})

    def list_all(self) -> list[JournalEntry]:
        rows = self._conn.execute(
            "SELECT id, date, description, document_type FROM journal_entries ORDER BY date DESC, id DESC"
        ).fetchall()
        return [self._load_entry(row) for row in rows]

    def _load_entry(self, row: sqlite3.Row) -> JournalEntry:
        lines_rows = self._conn.execute(
            "SELECT account_code, debit, credit, partner_id FROM journal_lines WHERE entry_id = ? ORDER BY id",
            (row["id"],),
        ).fetchall()
        lines = tuple(
            JournalLine(
                account_code=r["account_code"],
                debit=Decimal(str(r["debit"])),
                credit=Decimal(str(r["credit"])),
                partner_id=r["partner_id"],
            )
            for r in lines_rows
        )
        return JournalEntry(
            id=row["id"],
            date=date.fromisoformat(row["date"]),
            description=row["description"],
            document_type=DocumentType(row["document_type"]),
            lines=lines,
        )

from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timedelta, time
from pathlib import Path
from typing import Iterable, List, Tuple

DB_PATH = Path("/mnt/data/high_peak_bicycles.db")
DATE_FMT = "%Y-%m-%d %H:%M"


@dataclass
class RentalRequestItem:
    registration_number: str
    prepaid_amount: float


class HighPeakBicyclesSystem:
    """A small SQLite-based prototype for the High Peak Bicycles case study."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    # ---------- Database setup ----------
    def initialize_database(self) -> None:
        with closing(self.conn.cursor()) as cur:
            cur.executescript(
                """
                CREATE TABLE IF NOT EXISTS bicycles (
                    registration_number TEXT PRIMARY KEY,
                    bike_class TEXT NOT NULL,
                    make TEXT NOT NULL,
                    model TEXT NOT NULL,
                    frame_size TEXT NOT NULL,
                    frame_number TEXT NOT NULL,
                    date_of_purchase TEXT NOT NULL,
                    purchase_price REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Available',
                    selling_date TEXT,
                    selling_price REAL,
                    write_off_date TEXT,
                    notes TEXT
                );

                CREATE TABLE IF NOT EXISTS rental_rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bike_class TEXT NOT NULL,
                    period TEXT NOT NULL,
                    rate REAL NOT NULL,
                    effective_from TEXT NOT NULL,
                    effective_to TEXT,
                    UNIQUE(bike_class, period, effective_from)
                );

                CREATE TABLE IF NOT EXISTS rentals (
                    rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    telephone TEXT NOT NULL,
                    date_created TEXT NOT NULL,
                    time_out TEXT NOT NULL,
                    expected_time_back TEXT NOT NULL,
                    expected_period TEXT NOT NULL,
                    deposit_type TEXT NOT NULL,
                    total_prepaid_amount REAL NOT NULL,
                    total_deposit_amount REAL NOT NULL,
                    time_returned TEXT,
                    actual_charge REAL,
                    extra_charge REAL,
                    deposit_released INTEGER DEFAULT 0,
                    rental_status TEXT NOT NULL DEFAULT 'Open',
                    incident_notes TEXT
                );

                CREATE TABLE IF NOT EXISTS rental_items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rental_id INTEGER NOT NULL,
                    registration_number TEXT NOT NULL,
                    bike_class TEXT NOT NULL,
                    model TEXT NOT NULL,
                    prepaid_amount REAL NOT NULL,
                    actual_amount REAL,
                    item_status TEXT NOT NULL DEFAULT 'Rented',
                    incident_type TEXT,
                    incident_charge REAL DEFAULT 0,
                    incident_notes TEXT,
                    FOREIGN KEY (rental_id) REFERENCES rentals(rental_id),
                    FOREIGN KEY (registration_number) REFERENCES bicycles(registration_number)
                );
                """
            )
        self.conn.commit()

    def seed_sample_data(self) -> None:
        bikes = [
            ("MB001", "MB", "Trek", "Marlin 7", "M", "FRM001", "2025-05-01", 800.0),
            ("MB002", "MB", "Giant", "Talon 2", "L", "FRM002", "2025-06-15", 760.0),
            ("MB003", "MB", "Scott", "Aspect 960", "M", "FRM003", "2024-08-20", 780.0),
            ("AT001", "AT", "Specialized", "Sirrus X", "M", "FRM004", "2025-03-10", 700.0),
            ("AT002", "AT", "Cannondale", "Quick CX", "S", "FRM005", "2024-09-05", 690.0),
            ("TD001", "TD", "Orbit", "Gemini Tandem", "XL", "FRM006", "2024-04-12", 1200.0),
        ]
        rates = [
            ("MB", "Day", 18.0, "2026-01-01", None),
            ("MB", "Half-Day", 10.0, "2026-01-01", None),
            ("MB", "Late Rental", 6.0, "2026-01-01", None),
            ("AT", "Day", 20.0, "2026-01-01", None),
            ("AT", "Half-Day", 12.0, "2026-01-01", None),
            ("AT", "Late Rental", 8.0, "2026-01-01", None),
            ("TD", "Day", 30.0, "2026-01-01", None),
            ("TD", "Half-Day", 18.0, "2026-01-01", None),
            ("TD", "Late Rental", 12.0, "2026-01-01", None),
        ]

        with closing(self.conn.cursor()) as cur:
            cur.executemany(
                """
                INSERT OR IGNORE INTO bicycles (
                    registration_number, bike_class, make, model, frame_size,
                    frame_number, date_of_purchase, purchase_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                bikes,
            )
            cur.executemany(
                """
                INSERT OR IGNORE INTO rental_rates (
                    bike_class, period, rate, effective_from, effective_to
                ) VALUES (?, ?, ?, ?, ?)
                """,
                rates,
            )
        self.conn.commit()

    # ---------- Helpers ----------
    def _fetch_one(self, query: str, params: Tuple = ()) -> sqlite3.Row | None:
        with closing(self.conn.cursor()) as cur:
            cur.execute(query, params)
            return cur.fetchone()

    def _fetch_all(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        with closing(self.conn.cursor()) as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def get_rate(self, bike_class: str, period: str, when: datetime) -> float:
        row = self._fetch_one(
            """
            SELECT rate
            FROM rental_rates
            WHERE bike_class = ?
              AND period = ?
              AND effective_from <= ?
              AND (effective_to IS NULL OR effective_to >= ?)
            ORDER BY effective_from DESC
            LIMIT 1
            """,
            (bike_class, period, when.date().isoformat(), when.date().isoformat()),
        )
        if not row:
            raise ValueError(f"No rate found for class {bike_class} and period {period}")
        return float(row["rate"])

    def determine_period(self, start: datetime, end: datetime) -> str:
        duration_hours = (end - start).total_seconds() / 3600
        late_start = time(16, 0)
        late_end = time(19, 0)
        if start.time() >= late_start and end.time() <= late_end:
            return "Late Rental"
        if duration_hours <= 4:
            return "Half-Day"
        return "Day"

    def list_available_bicycles(self) -> List[sqlite3.Row]:
        return self._fetch_all(
            """
            SELECT registration_number, bike_class, make, model, status
            FROM bicycles
            WHERE status = 'Available'
            ORDER BY bike_class, registration_number
            """
        )

    # ---------- Core business operations ----------
    def create_rental(
        self,
        customer_name: str,
        telephone: str,
        time_out: datetime,
        expected_time_back: datetime,
        expected_period: str,
        deposit_type: str,
        items: Iterable[RentalRequestItem],
    ) -> int:
        items = list(items)
        if not 1 <= len(items) <= 4:
            raise ValueError("A rental must include between 1 and 4 bicycles.")

        with closing(self.conn.cursor()) as cur:
            for item in items:
                bike = self._fetch_one(
                    "SELECT registration_number, bike_class, model, status FROM bicycles WHERE registration_number = ?",
                    (item.registration_number,),
                )
                if not bike:
                    raise ValueError(f"Bicycle {item.registration_number} does not exist.")
                if bike["status"] != "Available":
                    raise ValueError(f"Bicycle {item.registration_number} is not available.")

            total_prepaid = sum(item.prepaid_amount for item in items)
            total_deposit = 20.0 * len(items)
            cur.execute(
                """
                INSERT INTO rentals (
                    customer_name, telephone, date_created, time_out, expected_time_back,
                    expected_period, deposit_type, total_prepaid_amount, total_deposit_amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    customer_name,
                    telephone,
                    time_out.strftime("%Y-%m-%d"),
                    time_out.strftime(DATE_FMT),
                    expected_time_back.strftime(DATE_FMT),
                    expected_period,
                    deposit_type,
                    total_prepaid,
                    total_deposit,
                ),
            )
            rental_id = int(cur.lastrowid)

            for item in items:
                bike = self._fetch_one(
                    "SELECT bike_class, model FROM bicycles WHERE registration_number = ?",
                    (item.registration_number,),
                )
                cur.execute(
                    """
                    INSERT INTO rental_items (
                        rental_id, registration_number, bike_class, model, prepaid_amount
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        rental_id,
                        item.registration_number,
                        bike["bike_class"],
                        bike["model"],
                        item.prepaid_amount,
                    ),
                )
                cur.execute(
                    "UPDATE bicycles SET status = 'Rented' WHERE registration_number = ?",
                    (item.registration_number,),
                )
        self.conn.commit()
        return rental_id

    def return_rental(self, rental_id: int, actual_return_time: datetime) -> None:
        rental = self._fetch_one(
            "SELECT * FROM rentals WHERE rental_id = ?",
            (rental_id,),
        )
        if not rental:
            raise ValueError(f"Rental {rental_id} was not found.")
        if rental["rental_status"] != "Open":
            raise ValueError(f"Rental {rental_id} is already closed.")

        time_out = datetime.strptime(rental["time_out"], DATE_FMT)
        actual_period = self.determine_period(time_out, actual_return_time)
        items = self._fetch_all(
            "SELECT * FROM rental_items WHERE rental_id = ?",
            (rental_id,),
        )

        actual_total = 0.0
        prepaid_total = float(rental["total_prepaid_amount"])
        with closing(self.conn.cursor()) as cur:
            for item in items:
                actual_amount = self.get_rate(item["bike_class"], actual_period, actual_return_time)
                actual_total += actual_amount
                cur.execute(
                    """
                    UPDATE rental_items
                    SET actual_amount = ?, item_status = 'Returned'
                    WHERE item_id = ?
                    """,
                    (actual_amount, item["item_id"]),
                )
                cur.execute(
                    "UPDATE bicycles SET status = 'Available' WHERE registration_number = ?",
                    (item["registration_number"],),
                )

            extra_charge = max(0.0, actual_total - prepaid_total)
            cur.execute(
                """
                UPDATE rentals
                SET time_returned = ?, actual_charge = ?, extra_charge = ?,
                    deposit_released = 1, rental_status = 'Closed'
                WHERE rental_id = ?
                """,
                (actual_return_time.strftime(DATE_FMT), actual_total, extra_charge, rental_id),
            )
        self.conn.commit()

    def record_incident(
        self,
        rental_id: int,
        registration_number: str,
        incident_type: str,
        notes: str,
        incident_date: datetime,
    ) -> None:
        rental = self._fetch_one("SELECT * FROM rentals WHERE rental_id = ?", (rental_id,))
        if not rental:
            raise ValueError(f"Rental {rental_id} was not found.")

        bike = self._fetch_one(
            "SELECT * FROM bicycles WHERE registration_number = ?",
            (registration_number,),
        )
        item = self._fetch_one(
            """
            SELECT ri.*, b.purchase_price
            FROM rental_items ri
            JOIN bicycles b ON b.registration_number = ri.registration_number
            WHERE ri.rental_id = ? AND ri.registration_number = ?
            """,
            (rental_id, registration_number),
        )
        if not item:
            raise ValueError("The bicycle is not attached to the selected rental.")

        if incident_type not in {"Abandoned", "Unrecovered"}:
            raise ValueError("incident_type must be 'Abandoned' or 'Unrecovered'.")

        incident_charge = 20.0 if incident_type == "Abandoned" else float(item["purchase_price"])
        bike_status = "Available" if incident_type == "Abandoned" else "Written Off"
        write_off_date = None if incident_type == "Abandoned" else (incident_date + timedelta(days=10)).date().isoformat()

        with closing(self.conn.cursor()) as cur:
            cur.execute(
                """
                UPDATE rental_items
                SET item_status = ?, incident_type = ?, incident_charge = ?, incident_notes = ?
                WHERE item_id = ?
                """,
                (incident_type, incident_type, incident_charge, notes, item["item_id"]),
            )
            cur.execute(
                """
                UPDATE bicycles
                SET status = ?, write_off_date = COALESCE(write_off_date, ?), notes = ?
                WHERE registration_number = ?
                """,
                (bike_status, write_off_date, notes, registration_number),
            )
            cur.execute(
                """
                UPDATE rentals
                SET time_returned = COALESCE(time_returned, ?),
                    actual_charge = COALESCE(actual_charge, 0) + ?,
                    extra_charge = COALESCE(extra_charge, 0) + ?,
                    rental_status = 'Incident',
                    incident_notes = COALESCE(incident_notes, '') || ?
                WHERE rental_id = ?
                """,
                (
                    incident_date.strftime(DATE_FMT),
                    incident_charge,
                    incident_charge,
                    f"\n{registration_number}: {incident_type} - {notes}",
                    rental_id,
                ),
            )
        self.conn.commit()

    # ---------- Reports ----------
    def print_inventory_report(self) -> str:
        rows = self._fetch_all(
            """
            SELECT registration_number, bike_class, make, model, status
            FROM bicycles
            ORDER BY bike_class, registration_number
            """
        )
        lines = ["\nINVENTORY REPORT", "-" * 65]
        for row in rows:
            lines.append(
                f"{row['registration_number']:<6} | {row['bike_class']:<2} | {row['make']:<12} | {row['model']:<15} | {row['status']}"
            )
        return "\n".join(lines)

    def print_daily_report(self, report_date: str) -> str:
        summary = self._fetch_one(
            """
            SELECT COUNT(*) AS rentals_count,
                   COALESCE(SUM(COALESCE(actual_charge, total_prepaid_amount)), 0) AS revenue
            FROM rentals
            WHERE date_created = ?
            """,
            (report_date,),
        )
        detail = self._fetch_all(
            """
            SELECT rental_id, customer_name, expected_period, rental_status,
                   total_prepaid_amount, COALESCE(actual_charge, total_prepaid_amount) AS actual_total
            FROM rentals
            WHERE date_created = ?
            ORDER BY rental_id
            """,
            (report_date,),
        )
        lines = [
            f"\nDAILY REPORT FOR {report_date}",
            "-" * 65,
            f"Number of rentals : {summary['rentals_count']}",
            f"Total revenue      : ${summary['revenue']:.2f}",
            "",
            "Rental details:",
        ]
        for row in detail:
            lines.append(
                f"Rental #{row['rental_id']}: {row['customer_name']} | {row['expected_period']} | {row['rental_status']} | ${row['actual_total']:.2f}"
            )
        return "\n".join(lines)

    def print_depreciation_report(self) -> str:
        rows = self._fetch_all(
            """
            SELECT registration_number, make, model, purchase_price, selling_price,
                   ROUND(COALESCE(purchase_price - selling_price, 0), 2) AS depreciation
            FROM bicycles
            WHERE selling_price IS NOT NULL
            ORDER BY depreciation DESC
            """
        )
        if not rows:
            return "\nDEPRECIATION REPORT\n------------------------------\nNo sold bicycles found yet."
        lines = ["\nDEPRECIATION REPORT", "-" * 65]
        for row in rows:
            lines.append(
                f"{row['registration_number']}: {row['make']} {row['model']} | bought ${row['purchase_price']:.2f} | sold ${row['selling_price']:.2f} | depreciation ${row['depreciation']:.2f}"
            )
        return "\n".join(lines)

    def sell_bicycle(self, registration_number: str, selling_date: str, selling_price: float) -> None:
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                """
                UPDATE bicycles
                SET status = 'Sold', selling_date = ?, selling_price = ?
                WHERE registration_number = ?
                """,
                (selling_date, selling_price, registration_number),
            )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()


# ---------- Demo runner ----------
def run_demo() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    system = HighPeakBicyclesSystem(DB_PATH)
    try:
        system.initialize_database()
        system.seed_sample_data()

        print("HIGH PEAK BICYCLES - PYTHON PROTOTYPE")
        print("=" * 65)
        print(system.print_inventory_report())

        rental_1 = system.create_rental(
            customer_name="Alice Johnson",
            telephone="07000 123456",
            time_out=datetime(2026, 4, 22, 9, 0),
            expected_time_back=datetime(2026, 4, 22, 13, 0),
            expected_period="Half-Day",
            deposit_type="Cash",
            items=[
                RentalRequestItem("MB001", 10.0),
                RentalRequestItem("AT001", 12.0),
            ],
        )
        print(f"\nCreated rental #{rental_1} for Alice Johnson.")
        system.return_rental(rental_1, datetime(2026, 4, 22, 17, 30))
        print(f"Rental #{rental_1} returned late. Extra charges were calculated automatically.")

        rental_2 = system.create_rental(
            customer_name="Brian Smith",
            telephone="07000 987654",
            time_out=datetime(2026, 4, 22, 16, 0),
            expected_time_back=datetime(2026, 4, 22, 19, 0),
            expected_period="Late Rental",
            deposit_type="Credit Card",
            items=[
                RentalRequestItem("MB002", 6.0),
                RentalRequestItem("MB003", 6.0),
            ],
        )
        print(f"Created rental #{rental_2} for Brian Smith.")
        system.record_incident(
            rental_id=rental_2,
            registration_number="MB002",
            incident_type="Abandoned",
            notes="Returned later by park warden.",
            incident_date=datetime(2026, 4, 22, 20, 30),
        )
        system.record_incident(
            rental_id=rental_2,
            registration_number="MB003",
            incident_type="Unrecovered",
            notes="Bike not recovered after 10 days; written off.",
            incident_date=datetime(2026, 4, 22, 20, 30),
        )
        print("Incident handling completed for rental #2.")

        system.sell_bicycle("AT002", "2026-04-22", 420.0)

        print(system.print_inventory_report())
        print(system.print_daily_report("2026-04-22"))
        print(system.print_depreciation_report())
    finally:
        system.close()


if __name__ == "__main__":
    run_demo()

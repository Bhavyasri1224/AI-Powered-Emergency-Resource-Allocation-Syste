from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(__file__).resolve().parent / "emergency.db"
HOSPITAL_CSV = ROOT / "data" / "hospitals.csv"


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with connect() as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS hospitals (
            id INTEGER PRIMARY KEY,
            hospital_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            available_beds INTEGER NOT NULL,
            icu_beds INTEGER NOT NULL,
            specializations TEXT NOT NULL,
            current_patient_load INTEGER NOT NULL,
            emergency_support INTEGER NOT NULL
        )""")
        count = connection.execute("SELECT COUNT(*) FROM hospitals").fetchone()[0]
        if count == 0:
            with HOSPITAL_CSV.open(newline="", encoding="utf-8") as source:
                for hospital in csv.DictReader(source):
                    connection.execute("""INSERT INTO hospitals
                        (hospital_name, latitude, longitude, available_beds, icu_beds,
                         specializations, current_patient_load, emergency_support)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (
                        hospital["hospital_name"], float(hospital["latitude"]), float(hospital["longitude"]),
                        int(hospital["available_beds"]), int(hospital["icu_beds"]), hospital["specializations"],
                        int(hospital["current_patient_load"]), int(hospital["emergency_support"].lower() == "true"),
                    ))


def list_hospitals() -> list[dict]:
    initialize_database()
    with connect() as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM hospitals ORDER BY id")]

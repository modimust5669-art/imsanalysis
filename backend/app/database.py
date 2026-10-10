import os
import sqlite3
import json
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "liptis_app.db")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn

@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                subtitle TEXT,
                destination TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                date_display TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'published', -- 'draft', 'published', 'archived'
                has_unpublished_changes INTEGER NOT NULL DEFAULT 0,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                published_at TEXT
            )
        """)

        # Flight Groups table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flight_groups (
                id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                name TEXT NOT NULL,
                airline TEXT NOT NULL,
                outbound_flight_number TEXT NOT NULL,
                departure_airport TEXT NOT NULL,
                departure_date TEXT NOT NULL,
                departure_time TEXT NOT NULL,
                arrival_airport TEXT NOT NULL,
                arrival_date TEXT NOT NULL,
                arrival_time TEXT NOT NULL,
                return_flight_number TEXT,
                return_departure_airport TEXT,
                return_departure_date TEXT,
                return_departure_time TEXT,
                return_arrival_airport TEXT,
                return_arrival_date TEXT,
                return_arrival_time TEXT,
                notes TEXT,
                display_order INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE
            )
        """)

        # Itinerary Entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itinerary_entries (
                id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                flight_group_id TEXT, -- NULL means Shared by ALL flight groups
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                title TEXT NOT NULL,
                location TEXT,
                description TEXT,
                category TEXT NOT NULL DEFAULT 'activity', -- 'flight', 'transfer', 'hotel', 'symposium', 'meal', 'prayer', 'culture', 'activity'
                meeting_point TEXT,
                transportation_notes TEXT,
                special_instructions TEXT,
                is_important INTEGER NOT NULL DEFAULT 0,
                display_order INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE,
                FOREIGN KEY (flight_group_id) REFERENCES flight_groups (id) ON DELETE CASCADE
            )
        """)

        # Fixed Topic / Content Sections table (strictly adhering to PDF topics)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_sections (
                id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                section_key TEXT NOT NULL,
                title TEXT NOT NULL,
                content_json TEXT NOT NULL,
                display_order INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE,
                UNIQUE(event_id, section_key)
            )
        """)

        # Guest Care Contacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                name TEXT NOT NULL,
                title TEXT NOT NULL,
                phone TEXT NOT NULL,
                whatsapp TEXT,
                category TEXT NOT NULL DEFAULT 'Guest Care',
                display_order INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE
            )
        """)

        # Audit Logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                event_id TEXT,
                action TEXT NOT NULL,
                admin_user TEXT NOT NULL,
                details TEXT,
                timestamp TEXT NOT NULL
            )
        """)

        # Admin Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'admin',
                created_at TEXT NOT NULL
            )
        """)

        # Admin Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_sessions (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES admin_users (id) ON DELETE CASCADE
            )
        """)

        conn.commit()

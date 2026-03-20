# ============================================================
# guardrails_db.py — Dynamic Guardrails Database
# SQLite mein rules store honge — no hardcoding!
# ============================================================

import sqlite3
import json

DB_PATH = "users.db"


def init_guardrails_db():
    """Create all guardrail tables if not exist + seed default data."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # --- Table 1: Plan Exclusions ---
    c.execute('''CREATE TABLE IF NOT EXISTS gr_exclusions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan TEXT NOT NULL,
        keyword TEXT NOT NULL,
        active INTEGER DEFAULT 1
    )''')

    # --- Table 2: Age Restrictions ---
    c.execute('''CREATE TABLE IF NOT EXISTS gr_age_restrictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        condition_name TEXT NOT NULL,
        keywords TEXT NOT NULL,
        min_age INTEGER NOT NULL,
        max_age INTEGER NOT NULL,
        message TEXT NOT NULL,
        active INTEGER DEFAULT 1
    )''')

    # --- Table 3: Prior Auth Triggers ---
    c.execute('''CREATE TABLE IF NOT EXISTS gr_prior_auth (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT NOT NULL,
        active INTEGER DEFAULT 1
    )''')

    # --- Table 4: Fraud Signals ---
    c.execute('''CREATE TABLE IF NOT EXISTS gr_fraud_signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        signal_name TEXT NOT NULL,
        keywords TEXT NOT NULL,
        message TEXT NOT NULL,
        active INTEGER DEFAULT 1
    )''')

    conn.commit()

    # Seed default data if tables are empty
    _seed_defaults(conn, c)
    conn.close()


def _seed_defaults(conn, c):
    """Seed default rules only if tables are empty."""

    # Exclusions
    c.execute("SELECT COUNT(*) FROM gr_exclusions")
    if c.fetchone()[0] == 0:
        exclusions = [
            ("Ayushman Bharat (PMJAY)", "cosmetic surgery"),
            ("Ayushman Bharat (PMJAY)", "cosmetic"),
            ("Ayushman Bharat (PMJAY)", "fertility treatment"),
            ("Ayushman Bharat (PMJAY)", "ivf"),
            ("Ayushman Bharat (PMJAY)", "self-inflicted"),
            ("Ayushman Bharat (PMJAY)", "self harm"),
            ("Ayushman Bharat (PMJAY)", "experimental drug"),
            ("Ayushman Bharat (PMJAY)", "lasik"),
            ("Ayushman Bharat (PMJAY)", "teeth whitening"),
            ("BSKY (Odisha)", "cosmetic"),
            ("BSKY (Odisha)", "dental cosmetic"),
            ("BSKY (Odisha)", "experimental"),
            ("BSKY (Odisha)", "fertility"),
            ("BSKY (Odisha)", "lasik"),
            ("BSKY (Odisha)", "self-inflicted"),
            ("ESIC", "cosmetic surgery"),
            ("ESIC", "experimental treatment"),
            ("ESIC", "self-inflicted injury"),
            ("ESIC", "fertility"),
            ("CGHS", "cosmetic"),
            ("CGHS", "experimental"),
            ("CGHS", "fertility treatment"),
            ("CGHS", "lasik"),
            ("CGHS", "self-inflicted"),
            ("Private PPO", "self-inflicted"),
            ("Private PPO", "experimental unapproved"),
        ]
        c.executemany(
            "INSERT INTO gr_exclusions (plan, keyword) VALUES (?, ?)", exclusions
        )

    # Age Restrictions
    c.execute("SELECT COUNT(*) FROM gr_age_restrictions")
    if c.fetchone()[0] == 0:
        age_rules = [
            ("Maternity", "delivery,pregnancy,maternity,prenatal,postnatal,c-section,caesarean",
             18, 55, "Maternity claims covered for patients aged 18–55 only."),
            ("Pediatric Surgery", "pediatric,paediatric,child surgery,neonatal",
             0, 18, "Pediatric procedures covered for patients under 18 years."),
            ("Joint Replacement", "knee replacement,hip replacement,joint replacement,total hip,total knee",
             40, 120, "Elective joint replacement approved for patients 40 years and above."),
        ]
        c.executemany(
            "INSERT INTO gr_age_restrictions (condition_name, keywords, min_age, max_age, message) VALUES (?,?,?,?,?)",
            age_rules
        )

    # Prior Auth
    c.execute("SELECT COUNT(*) FROM gr_prior_auth")
    if c.fetchone()[0] == 0:
        prior_auth = [
            ("stent",), ("angioplasty",), ("bypass",), ("cabg",),
            ("hip replacement",), ("knee replacement",), ("joint replacement",),
            ("organ transplant",), ("transplant",),
            ("cancer treatment",), ("chemotherapy",), ("radiation therapy",),
            ("icu admission",), ("intensive care",),
            ("neurosurgery",), ("brain surgery",), ("spinal surgery",),
            ("bariatric",), ("dialysis",), ("cochlear implant",),
            ("robotic surgery",), ("bone marrow transplant",),
        ]
        c.executemany("INSERT INTO gr_prior_auth (keyword) VALUES (?)", prior_auth)

    # Fraud Signals
    c.execute("SELECT COUNT(*) FROM gr_fraud_signals")
    if c.fetchone()[0] == 0:
        fraud = [
            ("Upcoding", "minor,simple,routine,basic,small",
             "Potential upcoding: simple diagnosis paired with complex procedure billing."),
            ("Unbundling", "separate billing,unbundle,individual components",
             "Potential unbundling of procedures detected."),
        ]
        c.executemany(
            "INSERT INTO gr_fraud_signals (signal_name, keywords, message) VALUES (?,?,?)",
            fraud
        )

    conn.commit()


# ============================================================
# READ FUNCTIONS
# ============================================================

def get_exclusions(plan=None, active_only=True):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if plan:
        query = "SELECT * FROM gr_exclusions WHERE plan=?"
        params = [plan]
        if active_only:
            query += " AND active=1"
        c.execute(query, params)
    else:
        query = "SELECT * FROM gr_exclusions"
        if active_only:
            query += " WHERE active=1"
        c.execute(query)
    rows = c.fetchall()
    conn.close()
    return rows


def get_age_restrictions(active_only=True):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = "SELECT * FROM gr_age_restrictions"
    if active_only:
        query += " WHERE active=1"
    c.execute(query)
    rows = c.fetchall()
    conn.close()
    return rows


def get_prior_auth_triggers(active_only=True):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = "SELECT * FROM gr_prior_auth"
    if active_only:
        query += " WHERE active=1"
    c.execute(query)
    rows = c.fetchall()
    conn.close()
    return rows


def get_fraud_signals(active_only=True):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = "SELECT * FROM gr_fraud_signals"
    if active_only:
        query += " WHERE active=1"
    c.execute(query)
    rows = c.fetchall()
    conn.close()
    return rows


# ============================================================
# CRUD FUNCTIONS
# ============================================================

def add_exclusion(plan, keyword):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO gr_exclusions (plan, keyword) VALUES (?,?)", (plan, keyword.lower()))
    conn.commit()
    conn.close()

def delete_exclusion(rule_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM gr_exclusions WHERE id=?", (rule_id,))
    conn.commit()
    conn.close()

def toggle_exclusion(rule_id, active):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE gr_exclusions SET active=? WHERE id=?", (active, rule_id))
    conn.commit()
    conn.close()


def add_age_restriction(condition_name, keywords, min_age, max_age, message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO gr_age_restrictions (condition_name, keywords, min_age, max_age, message) VALUES (?,?,?,?,?)",
        (condition_name, keywords.lower(), min_age, max_age, message)
    )
    conn.commit()
    conn.close()

def delete_age_restriction(rule_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM gr_age_restrictions WHERE id=?", (rule_id,))
    conn.commit()
    conn.close()

def toggle_age_restriction(rule_id, active):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE gr_age_restrictions SET active=? WHERE id=?", (active, rule_id))
    conn.commit()
    conn.close()


def add_prior_auth(keyword):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO gr_prior_auth (keyword) VALUES (?)", (keyword.lower(),))
    conn.commit()
    conn.close()

def delete_prior_auth(rule_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM gr_prior_auth WHERE id=?", (rule_id,))
    conn.commit()
    conn.close()

def toggle_prior_auth(rule_id, active):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE gr_prior_auth SET active=? WHERE id=?", (active, rule_id))
    conn.commit()
    conn.close()


def add_fraud_signal(signal_name, keywords, message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO gr_fraud_signals (signal_name, keywords, message) VALUES (?,?,?)",
        (signal_name, keywords.lower(), message)
    )
    conn.commit()
    conn.close()

def delete_fraud_signal(rule_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM gr_fraud_signals WHERE id=?", (rule_id,))
    conn.commit()
    conn.close()

def toggle_fraud_signal(rule_id, active):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE gr_fraud_signals SET active=? WHERE id=?", (active, rule_id))
    conn.commit()
    conn.close()
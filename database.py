"""SQLite storage for user accounts and resident profiles."""
import csv
import hashlib
import hmac
import os
import sqlite3
import shutil
from pathlib import Path
from contextlib import contextmanager
from datetime import date, datetime

import resources

DB_PATH = resources.DATA / "barangay.db"
BACKUP_DIR = Path("backups")

SEX = ["Male", "Female"]
CIVIL_STATUS = ["Single", "Married", "Widowed", "Separated", "Live-in"]
EDUCATION = ["No formal education", "Elementary", "High School", "Senior High School",
             "Vocational/Technical", "College", "Post Graduate"]

FIELDS = ["last_name", "first_name", "middle_name", "ext_name", "birth_date", "birth_place",
          "sex", "civil_status", "education", "occupation", "address", "contact", "email"]


@contextmanager
def _conn():
    resources.DATA.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            pw_hash TEXT NOT NULL,
            pw_salt TEXT NOT NULL,
            key_hash TEXT NOT NULL,
            key_salt TEXT NOT NULL,
            created_at TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Staff'
        );

        CREATE TABLE IF NOT EXISTS residents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            middle_name TEXT DEFAULT '',
            ext_name TEXT DEFAULT '',
            birth_date TEXT NOT NULL,
            birth_place TEXT NOT NULL,
            sex TEXT NOT NULL,
            civil_status TEXT NOT NULL,
            education TEXT DEFAULT '',
            occupation TEXT DEFAULT '',
            address TEXT NOT NULL,
            contact TEXT DEFAULT '',
            email TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_name TEXT NOT NULL,
            user_role TEXT NOT NULL,
            action TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)

        columns = [
            row["name"]
            for row in c.execute(
                "PRAGMA table_info(users)"
            ).fetchall()
        ]

        if "role" not in columns:
            c.execute(
                "ALTER TABLE users "
                "ADD COLUMN role TEXT NOT NULL DEFAULT 'Staff'"
            )

    ensure_admin_account()


# ---- accounts -----------------------------------------------------------
def _hash(secret, salt):
    return hashlib.pbkdf2_hmac("sha256", secret.encode(), salt, 200_000).hex()


def _new_hash(secret):
    salt = os.urandom(16)
    return _hash(secret, salt), salt.hex()


def _matches(secret, stored_hash, salt_hex):
    return hmac.compare_digest(_hash(secret, bytes.fromhex(salt_hex)), stored_hash)

def ensure_admin_account():
    admin_email = "admin"
    admin_password = "admin123"
    recovery_key = "admin123"

    with _conn() as c:

        # Make EVERY existing account Staff first
        c.execute(
            "UPDATE users SET role='Staff'"
        )

        # Check if the fixed admin account already exists
        existing = c.execute(
            "SELECT id FROM users WHERE LOWER(email)=?",
            (admin_email,)
        ).fetchone()

        if existing:
            # Make only the fixed admin account Admin
            c.execute(
                "UPDATE users SET role='Admin' WHERE id=?",
                (existing["id"],)
            )

        else:
            # Create the fixed admin account
            pw_hash, pw_salt = _new_hash(admin_password)
            key_hash, key_salt = _new_hash(recovery_key)

            c.execute(
                """
                INSERT INTO users (
                    full_name,
                    email,
                    pw_hash,
                    pw_salt,
                    key_hash,
                    key_salt,
                    created_at,
                    role
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "Administrator",
                    admin_email,
                    pw_hash,
                    pw_salt,
                    key_hash,
                    key_salt,
                    datetime.now().isoformat(timespec="seconds"),
                    "Admin"
                )
            )


def create_user(full_name, email, password, recovery_key):
    pw_hash, pw_salt = _new_hash(password)
    key_hash, key_salt = _new_hash(recovery_key)

    try:
        with _conn() as c:

            role = "Staff"

            c.execute(
                "INSERT INTO users "
                "(full_name, email, pw_hash, pw_salt, key_hash, key_salt, created_at, role) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (
                    full_name,
                    email.lower(),
                    pw_hash,
                    pw_salt,
                    key_hash,
                    key_salt,
                    datetime.now().isoformat(timespec="seconds"),
                    role
                )
            )

        return True

    except sqlite3.IntegrityError:
        return False


def has_users():
    with _conn() as c:
        return c.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0


def check_login(email, password):
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE email=?", (email.lower(),)).fetchone()
    if row and _matches(password, row["pw_hash"], row["pw_salt"]):
        return dict(row)
    return None


def reset_password(email, recovery_key, new_password):
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE email=?", (email.lower(),)).fetchone()
        if not row or not _matches(recovery_key, row["key_hash"], row["key_salt"]):
            return False
        pw_hash, pw_salt = _new_hash(new_password)
        c.execute("UPDATE users SET pw_hash=?, pw_salt=? WHERE id=?",
                  (pw_hash, pw_salt, row["id"]))
    return True
def get_users():
    with _conn() as c:
        rows = c.execute(
            "SELECT id, full_name, email, role, created_at "
            "FROM users ORDER BY id"
        ).fetchall()

    return [dict(row) for row in rows]


def get_user(user_id):
    with _conn() as c:
        row = c.execute(
            "SELECT id, full_name, email, role, created_at "
            "FROM users WHERE id=?",
            (user_id,)
        ).fetchone()

    return dict(row) if row else None


def count_users():
    with _conn() as c:
        return c.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]


def count_admins():
    with _conn() as c:
        return c.execute(
            "SELECT COUNT(*) FROM users WHERE role='Admin'"
        ).fetchone()[0]


def update_user_role(user_id, role):
    if role not in ("Admin", "Staff"):
        return False

    with _conn() as c:
        c.execute(
            "UPDATE users SET role=? WHERE id=?",
            (role, user_id)
        )

    return True


def delete_user(user_id):
    with _conn() as c:
        c.execute(
            "DELETE FROM users WHERE id=?",
            (user_id,)
        )

def add_activity(user_id, user_name, user_role, action, description):
    with _conn() as c:
        c.execute(
            """
            INSERT INTO activity_logs (
                user_id,
                user_name,
                user_role,
                action,
                description,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                user_name,
                user_role,
                action,
                description,
                datetime.now().isoformat(timespec="seconds")
            )
        )


def get_activity_logs():
    with _conn() as c:
        rows = c.execute(
            """
            SELECT *
            FROM activity_logs
            ORDER BY id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]

# ---- residents ----------------------------------------------------------
def fmt_id(rid):
    return f"R{int(rid):04d}"


def parse_id(text):
    digits = "".join(ch for ch in text if ch.isdigit())
    return int(digits) if digits else None


def age_of(birth_iso, today=None):
    today = today or date.today()
    b = date.fromisoformat(birth_iso)
    return today.year - b.year - ((today.month, today.day) < (b.month, b.day))


def full_name(r):
    mid = f" {r['middle_name'][0]}." if r["middle_name"] else ""
    ext = f" {r['ext_name']}" if r["ext_name"] else ""
    return f"{r['last_name']}, {r['first_name']}{mid}{ext}"


def add_resident(data):
    now = datetime.now().isoformat(timespec="seconds")
    cols = FIELDS + ["created_at", "updated_at"]
    vals = [data.get(f, "") for f in FIELDS] + [now, now]
    with _conn() as c:
        cur = c.execute(f"INSERT INTO residents ({','.join(cols)}) "
                        f"VALUES ({','.join('?' * len(cols))})", vals)
        return cur.lastrowid


def update_resident(rid, data):
    sets = ", ".join(f"{f}=?" for f in FIELDS) + ", updated_at=?"
    vals = [data.get(f, "") for f in FIELDS] + [datetime.now().isoformat(timespec="seconds"), rid]
    with _conn() as c:
        c.execute(f"UPDATE residents SET {sets} WHERE id=?", vals)


def delete_resident(rid):
    with _conn() as c:
        c.execute("DELETE FROM residents WHERE id=?", (rid,))

        rows = c.execute(
            "SELECT id FROM residents ORDER BY id"
        ).fetchall()

        new_id = 1

        for row in rows:
            old_id = row["id"]

            if old_id != new_id:
                c.execute(
                    "UPDATE residents SET id=? WHERE id=?",
                    (-new_id, old_id)
                )

            new_id += 1

        c.execute(
            "UPDATE residents SET id = -id WHERE id < 0"
        )

        c.execute(
            "DELETE FROM sqlite_sequence WHERE name='residents'"
        )

        if rows:
            c.execute(
                "INSERT INTO sqlite_sequence(name, seq) VALUES('residents', ?)",
                (len(rows),)
            )


def get_resident(rid):
    with _conn() as c:
        row = c.execute("SELECT * FROM residents WHERE id=?", (rid,)).fetchone()
    return dict(row) if row else None


def _search_clause(term):
    term = term.strip()
    if not term:
        return "", []
    like = f"%{term}%"
    clause = (" WHERE last_name LIKE ? OR first_name LIKE ? OR middle_name LIKE ?"
              " OR address LIKE ? OR occupation LIKE ? OR contact LIKE ?")
    args = [like] * 6
    rid = parse_id(term)
    if rid is not None and term.upper().lstrip("R").isdigit():
        clause += " OR id=?"
        args.append(rid)
    return clause, args


def count_residents(term=""):
    clause, args = _search_clause(term)
    with _conn() as c:
        return c.execute(f"SELECT COUNT(*) FROM residents{clause}", args).fetchone()[0]


def list_residents(term="", limit=10, offset=0):
    clause, args = _search_clause(term)
    with _conn() as c:
        rows = c.execute(f"SELECT * FROM residents{clause} ORDER BY last_name, first_name, id "
                         f"LIMIT ? OFFSET ?", args + [limit, offset]).fetchall()
    return [dict(r) for r in rows]


def all_residents():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM residents ORDER BY id").fetchall()]


def export_csv(path):
    rows = all_residents()
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["ID", "Last name", "First name", "Middle name", "Ext", "Birth date", "Age",
                    "Birth place", "Sex", "Civil status", "Education", "Occupation", "Address",
                    "Contact", "Email"])
        for r in rows:
            w.writerow([fmt_id(r["id"]), r["last_name"], r["first_name"], r["middle_name"],
                        r["ext_name"], r["birth_date"], age_of(r["birth_date"]), r["birth_place"],
                        r["sex"], r["civil_status"], r["education"], r["occupation"],
                        r["address"], r["contact"], r["email"]])
    return len(rows)


def statistics():
    rows = all_residents()
    today = date.today()
    stats = {"total": len(rows), "sex": {}, "civil": {}, "education": {},
             "age": {"0-17": 0, "18-29": 0, "30-44": 0, "45-59": 0, "60+": 0},
             "seniors": 0, "new_this_month": 0}
    for r in rows:
        a = age_of(r["birth_date"], today)
        stats["sex"][r["sex"]] = stats["sex"].get(r["sex"], 0) + 1
        stats["civil"][r["civil_status"]] = stats["civil"].get(r["civil_status"], 0) + 1
        if r["education"]:
            stats["education"][r["education"]] = stats["education"].get(r["education"], 0) + 1
        bucket = ("0-17" if a < 18 else "18-29" if a < 30 else "30-44" if a < 45
                  else "45-59" if a < 60 else "60+")
        stats["age"][bucket] += 1
        stats["seniors"] += a >= 60
        stats["new_this_month"] += r["created_at"][:7] == today.strftime("%Y-%m")
    return stats

def create_backup():
    BACKUP_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    backup_path = (
        BACKUP_DIR /
        f"barangay_backup_{timestamp}.db"
    )

    source = sqlite3.connect(DB_PATH)
    destination = sqlite3.connect(backup_path)

    try:
        source.backup(destination)
    finally:
        destination.close()
        source.close()

    return backup_path

def get_backups():
    BACKUP_DIR.mkdir(exist_ok=True)

    backups = []

    for path in BACKUP_DIR.glob("*.db"):
        created = datetime.fromtimestamp(
            path.stat().st_mtime
        )

        backups.append({
            "name": path.name,
            "path": path,
            "created_at": created
        })

    backups.sort(
        key=lambda item: item["created_at"],
        reverse=True
    )

    return backups


def restore_backup(backup_path):
    backup_path = Path(backup_path)

    if not backup_path.exists():
        return False

    BACKUP_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    safety_backup = (
        BACKUP_DIR /
        f"pre_restore_{timestamp}.db"
    )

    # Create a safety copy of the current database
    if DB_PATH.exists():
        shutil.copy2(
            DB_PATH,
            safety_backup
        )

    # Replace current database with selected backup
    shutil.copy2(
        backup_path,
        DB_PATH
    )

    return True


def delete_backup(backup_path):
    backup_path = Path(backup_path)

    if not backup_path.exists():
        return False

    backup_path.unlink()

    return True
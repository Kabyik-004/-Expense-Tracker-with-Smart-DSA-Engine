import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "instance", "expense_tracker.db")

if not os.path.exists(db_path):
    print("No existing database found — will be created fresh on startup.")
    exit(0)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(users)")
cols = {row[1] for row in cursor.fetchall()}

if "avatar" not in cols:
    print("Adding avatar column to users table...")
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN avatar TEXT")
        conn.commit()
        print("Done.")
    except Exception as e:
        print(f"Failed: {e}")
else:
    print("avatar column already exists.")

cursor.execute("PRAGMA table_info(budgets)")
if not cursor.fetchall():
    print("Creating budgets table...")
    cursor.execute("""
        CREATE TABLE budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            amount FLOAT NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """)
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_user_category_month_year ON budgets(user_id, category_id, month, year)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_budgets_user_month_year ON budgets(user_id, month, year)")
    conn.commit()
    print("Done.")
else:
    print("budgets table already exists.")

cursor.execute("PRAGMA table_info(activity_logs)")
if not cursor.fetchall():
    print("Creating activity_logs table...")
    cursor.execute("""
        CREATE TABLE activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            action VARCHAR(50) NOT NULL,
            entity_type VARCHAR(50) NOT NULL,
            entity_id INTEGER,
            details VARCHAR(500),
            created_at DATETIME NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_activity_logs_user_id ON activity_logs(user_id)")
    conn.commit()
    print("Done.")
else:
    print("activity_logs table already exists.")

conn.close()
print("Migration complete.")

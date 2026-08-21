"""Versioned PostgreSQL migrations for Semira Fashion.

The application creates only its base tables at startup. All changes to an
existing schema belong in a numbered SQL file under database/migrations/.
"""

from pathlib import Path


MIGRATIONS_DIR = Path(__file__).with_name("migrations")


def run_migrations(conn):
    """Apply each pending numbered migration in one transaction."""
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
            """
        )
        cur.execute("SELECT version FROM schema_migrations")
        applied = {row[0] for row in cur.fetchall()}

        files = sorted(
            path for path in MIGRATIONS_DIR.glob("*.sql")
            if path.name[:1].isdigit()
        )
        for path in files:
            version = path.stem
            if version in applied:
                continue
            sql = path.read_text(encoding="utf-8")
            cur.execute(sql)
            cur.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s)",
                (version,),
            )

    conn.commit()
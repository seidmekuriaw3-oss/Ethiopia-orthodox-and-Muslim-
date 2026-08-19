"""Read-only advertisement health check for the current Flask/PostgreSQL app."""

from app import app
from database.db import get_db


def fix_app_routes():
    """Verify that the current admin advertisement routes are registered."""
    routes = {rule.rule for rule in app.url_map.iter_rules()}
    required = {"/admin/ads", "/admin/ads/create"}
    missing = sorted(required - routes)
    if missing:
        print(f"Missing advertisement routes: {', '.join(missing)}")
        return False
    print("Advertisement routes are registered.")
    return True


def verify_database_structure():
    """Verify the PostgreSQL advertisements table and its key columns."""
    cursor = get_db().cursor()
    cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'advertisements'
        """
    )
    columns = {row["column_name"] for row in cursor.fetchall()}
    required = {"title", "description", "image", "is_active"}
    missing = sorted(required - columns)
    if missing:
        print(f"Missing advertisement columns: {', '.join(missing)}")
        return False
    print("PostgreSQL advertisements table is valid.")
    return True


if __name__ == "__main__":
    fix_app_routes()
    verify_database_structure()
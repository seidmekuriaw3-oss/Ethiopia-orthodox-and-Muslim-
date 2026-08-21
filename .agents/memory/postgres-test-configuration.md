---
name: PostgreSQL test configuration
description: Test-suite boundary between the current PostgreSQL contract and retired legacy tests.
---

The current Flask application tests must use PostgreSQL. The shared fixture accepts an optional `TEST_DATABASE_URL` for isolation, while tests marked `legacy` remain excluded by default because they target the retired SQLite/Furniture contract.

**Why:** The application no longer supports SQLite, and an in-memory SQLite fixture made tests appear valid while exercising a database contract the app cannot run.

**How to apply:** Run `pytest -q` for the default suite or `pytest -q -m postgres` for the explicit current contract. Never add `DATABASE_PATH`, `sqlite://`, or `:memory:` to the live fixture.
# Test suites

The current application uses PostgreSQL only. The default pytest command
excludes the tests marked `legacy`, which belong to the retired SQLite/Furniture
application contract:

```bash
pytest -q
```

Run only the current PostgreSQL contract tests with:

```bash
pytest -q -m postgres
```

For isolation, provide a separate PostgreSQL database before running tests:

```bash
TEST_DATABASE_URL=postgresql://... pytest -q -m postgres
```

Do not use `DATABASE_PATH`, `sqlite://`, or `:memory:` for the current app.
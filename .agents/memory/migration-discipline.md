---
name: Migration discipline
description: Project rule for PostgreSQL schema changes.
---

PostgreSQL schema upgrades, indexes, and foreign-key changes are versioned SQL migrations. Application startup may create the migration-history table and apply pending numbered files, but must not contain ad hoc schema mutations.

**Why:** Runtime DDL made schema evolution implicit, repeated on every worker startup, and difficult to audit or reproduce across environments.

**How to apply:** Add the next numbered SQL file for every future schema change; keep the migration runner transactional and record each applied version in `schema_migrations`.
---
name: Live contract test separation
description: How this project keeps retired application tests visible without letting them define current PostgreSQL behavior.
---

Retired SQLite/Furniture tests remain available as explicitly marked `legacy` tests, while the default suite validates the current PostgreSQL routes, category filtering, cart rendering, and product assets.

**Why:** The old tests assert schemas and APIs that no longer exist; silently deleting or adapting them would hide the migration boundary and make failures misleading.

**How to apply:** Add new behavior checks to the live contract suite. Only run or modify the legacy suite when intentionally working on historical compatibility.
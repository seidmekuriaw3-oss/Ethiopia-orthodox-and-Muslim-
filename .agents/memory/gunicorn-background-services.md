---
name: Gunicorn background services
description: Production WSGI startup must initialize scheduler and webhook work exactly once across multiple workers.
---

The production WSGI entrypoint must initialize background services; relying only on the direct `app.py` entrypoint silently disables scheduled jobs under Gunicorn. Multi-worker servers also need an inter-process ownership guard so daily jobs and webhook registration are not duplicated.

**Why:** The development server calls the background startup function directly, but Gunicorn imports the WSGI module instead. Without a WSGI startup hook, the daily digest never runs in production; without a lock, every worker can schedule duplicate jobs.

**How to apply:** Whenever background tasks are added or the WSGI/Gunicorn entrypoint changes, verify one worker owns the scheduler and webhook initialization, then check startup logs and a live health route.
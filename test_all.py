"""Compatibility test entrypoint for the current application.

The historical version tested the retired SQLite/Furniture application.
Use pytest so this command runs the current PostgreSQL live-contract suite.
"""

import pytest


if __name__ == "__main__":
    raise SystemExit(pytest.main(["-q"]))
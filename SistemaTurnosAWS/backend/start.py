"""Production entrypoint with bounded database/migration retries."""

import logging
import os
import subprocess
import sys
import time

from sqlalchemy import create_engine, text

from app.database import DATABASE_URL


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("backend.startup")


def migrate_with_retries() -> None:
    attempts = int(os.getenv("DB_STARTUP_ATTEMPTS", "12"))
    delay = float(os.getenv("DB_STARTUP_DELAY_SECONDS", "5"))

    for attempt in range(1, attempts + 1):
        try:
            # Keep a PostgreSQL advisory lock for the whole Alembic process.
            # This prevents two tasks in a rolling deployment from applying the
            # same migration concurrently.
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            with engine.connect() as connection:
                if connection.dialect.name == "postgresql":
                    connection.execute(text("SELECT pg_advisory_lock(724867321)"))
                subprocess.run(
                    [sys.executable, "-m", "alembic", "upgrade", "head"],
                    check=True,
                )
                if connection.dialect.name == "postgresql":
                    connection.execute(text("SELECT pg_advisory_unlock(724867321)"))
            engine.dispose()
            logger.info("Database migrations completed")
            return
        except Exception:
            logger.exception("Database migration attempt %s/%s failed", attempt, attempts)
            if attempt == attempts:
                raise
            time.sleep(delay)


if __name__ == "__main__":
    migrate_with_retries()
    os.execvp(
        sys.executable,
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--proxy-headers",
        ],
    )

import os
import subprocess
import sys


def test_rds_password_is_url_encoded():
    env = os.environ.copy()
    env.pop("DATABASE_URL", None)
    env.update(
        DB_HOST="database.internal",
        DB_PORT="5432",
        DB_NAME="turnosdb",
        DB_USER="turnos user",
        DB_PASSWORD="p@ss/word:#%",
    )
    result = subprocess.run(
        [sys.executable, "-c", "from app.database import DATABASE_URL; print(DATABASE_URL)"],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "turnos+user:p%40ss%2Fword%3A%23%25@database.internal" in result.stdout

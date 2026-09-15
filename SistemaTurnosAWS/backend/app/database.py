from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL and os.getenv("DB_HOST"):
    # RDS managed passwords can contain URL-reserved characters (for example
    # ``@``, ``/`` or ``#``).  Interpolating the secret without escaping it
    # makes SQLAlchemy parse part of the password as the host/path and causes
    # every ECS task to fail during startup.
    user = quote_plus(os.getenv("DB_USER", "postgres"))
    password = quote_plus(os.getenv("DB_PASSWORD", ""))
    DATABASE_URL = (
        f"postgresql://{user}:{password}@{os.environ['DB_HOST']}:"
        f"{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'turnosdb')}"
    )

if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada")

if DATABASE_URL == "sqlite:///:memory:":
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
elif DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "10"))},
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

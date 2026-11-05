import logging
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("vidhicms.database")

Base = declarative_base()


def ensure_mysql_database_exists() -> bool:
    """Create the MySQL database (lawfirm_db) with UTF8MB4 charset if it does not already exist."""
    db_url_str = settings.database_url
    if not db_url_str.startswith("mysql"):
        return True

    try:
        parsed = make_url(db_url_str)
        host = parsed.host or settings.MYSQL_HOST
        port = parsed.port or settings.MYSQL_PORT
        user = parsed.username or settings.MYSQL_USER
        password = parsed.password or settings.MYSQL_PASSWORD
        db_name = parsed.database or settings.MYSQL_DATABASE

        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset="utf8mb4",
            connect_timeout=10,
        )
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                )
            conn.commit()
            print(f"[MySQL] Connected to MySQL ({host}:{port} as '{user}') -> Database '{db_name}' ready.")
            return True
        finally:
            conn.close()
    except Exception as exc:
        logger.warning("Could not auto-create or verify MySQL database (%s).", exc)
        # Still return True if DATABASE_URL_OVERRIDE is explicitly provided so SQLAlchemy connects directly
        if settings.DATABASE_URL_OVERRIDE:
            return True
        return False


def build_engine():
    mysql_ok = ensure_mysql_database_exists()
    db_url = settings.database_url
    if not mysql_ok and not settings.DATABASE_URL_OVERRIDE:
        fallback_path = settings.UPLOAD_DIR.parent.parent.parent / "lawfirm_fallback.db"
        db_url = f"sqlite:///{fallback_path}"
        logger.warning("Using fallback SQLite database at %s because MySQL was unreachable.", fallback_path)

    if db_url.startswith("sqlite"):
        return create_engine(db_url, connect_args={"check_same_thread": False})
    return create_engine(
        db_url,
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_size=10,
        max_overflow=20,
    )


engine = build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

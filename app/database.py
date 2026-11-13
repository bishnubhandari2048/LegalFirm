import logging
import pymysql
from sqlalchemy import create_engine, inspect, text
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


def _run_schema_upgrade():
    """Internal helper to upgrade existing tables to add tenant_id and multi-tenant columns."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    tenant_scoped_tables = [
        "system_module_configs",
        "staff_members",
        "clients",
        "legal_cases",
        "hearings",
        "payment_records",
        "case_documents",
        "corporate_entities",
        "compliance_activities",
    ]

    with engine.begin() as conn:
        for tbl in tenant_scoped_tables:
            if tbl in existing_tables:
                cols = [c["name"] for c in inspector.get_columns(tbl)]
                if "tenant_id" not in cols:
                    conn.execute(text(f"ALTER TABLE `{tbl}` ADD COLUMN `tenant_id` INTEGER NOT NULL DEFAULT 1"))
                    logger.info("Added tenant_id column to %s", tbl)

        if "staff_members" in existing_tables:
            staff_cols = [c["name"] for c in inspector.get_columns("staff_members")]
            if "is_superadmin" not in staff_cols:
                conn.execute(text("ALTER TABLE `staff_members` ADD COLUMN `is_superadmin` BOOLEAN NOT NULL DEFAULT 0"))

        if "legal_cases" in existing_tables:
            case_cols = [c["name"] for c in inspector.get_columns("legal_cases")]
            for sulka_col in ["mudda_lekhan_sulka", "per_peshi_sulka", "waris_sulka", "court_dastur_sulka"]:
                if sulka_col not in case_cols:
                    conn.execute(text(f"ALTER TABLE `legal_cases` ADD COLUMN `{sulka_col}` FLOAT NOT NULL DEFAULT 0"))

        # Drop old single-tenant unique constraints/indexes so multiple tenants can use the same module_key, case_number, etc.
        legacy_unique_cols = {
            "system_module_configs": "module_key",
            "legal_cases": "case_number",
            "payment_records": "receipt_number",
            "corporate_entities": "ocr_registration_no",
        }
        for tbl, col_name in legacy_unique_cols.items():
            if tbl not in existing_tables:
                continue
            indexes = inspector.get_indexes(tbl)
            existing_idx_names = {i.get("name") for i in indexes}
            for idx in indexes:
                if idx.get("unique") and col_name in (idx.get("column_names") or []):
                    idx_name = idx["name"]
                    mt_idx_name = f"ix_{tbl}_{col_name}_mt"
                    try:
                        if engine.url.drivername.startswith("mysql"):
                            conn.execute(text(f"ALTER TABLE `{tbl}` DROP INDEX `{idx_name}`"))
                            if mt_idx_name not in existing_idx_names:
                                conn.execute(text(f"CREATE INDEX `{mt_idx_name}` ON `{tbl}` (`{col_name}`)"))
                        else:
                            conn.execute(text(f"DROP INDEX IF EXISTS `{idx_name}`"))
                            conn.execute(text(f"CREATE INDEX IF NOT EXISTS `{mt_idx_name}` ON `{tbl}` (`{col_name}`)"))
                    except Exception:
                        pass


def upgrade_schema_for_multitenancy():
    """Safely upgrade schema using a MySQL advisory lock to prevent concurrent DDL collisions across workers."""
    if engine.url.drivername.startswith("mysql"):
        with engine.connect() as lock_conn:
            lock_conn.execute(text("SELECT GET_LOCK('vidhi_lawfirm_ddl_lock', 60)"))
            try:
                Base.metadata.create_all(bind=engine)
                _run_schema_upgrade()
                Base.metadata.create_all(bind=engine)
            finally:
                lock_conn.execute(text("SELECT RELEASE_LOCK('vidhi_lawfirm_ddl_lock')"))
    else:
        Base.metadata.create_all(bind=engine)
        _run_schema_upgrade()
        Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

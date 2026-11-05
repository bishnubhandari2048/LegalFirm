import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    PROJECT_NAME: str = "विधि व्यवस्थापन प्रणाली | Law Firm Management System"
    VERSION: str = "1.0.0"

    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "digyantra")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "P@ssw0rDigyantra")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "lawfirm_db")

    # Optional full SQLAlchemy URL (e.g. mysql+pymysql://digyantra:P%40ssw0rDigyantra@localhost:3306/lawfirm_db)
    DATABASE_URL_OVERRIDE: str | None = os.getenv("DATABASE_URL")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "vidhi-law-firm-nepal-super-secret-jwt-key-2083")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    APP_PORT: int = int(os.getenv("APP_PORT", "8080"))

    UPLOAD_DIR: Path = BASE_DIR / "app" / "static" / "uploads"

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL_OVERRIDE:
            url = self.DATABASE_URL_OVERRIDE.strip()
            if "charset=" not in url and url.startswith("mysql"):
                sep = "&" if "?" in url else "?"
                url = f"{url}{sep}charset=utf8mb4"
            return url
        encoded_user = quote_plus(self.MYSQL_USER)
        encoded_pw = quote_plus(self.MYSQL_PASSWORD)
        return (
            f"mysql+pymysql://{encoded_user}:{encoded_pw}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
        )


settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

import sys
import uvicorn
from app.config import settings

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(f"Starting Vidhi Law Firm Management System on http://127.0.0.1:{settings.APP_PORT}")
    uvicorn.run("app.main:app", host="127.0.0.1", port=settings.APP_PORT, reload=False)

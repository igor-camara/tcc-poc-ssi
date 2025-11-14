from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

class Settings:
    def __init__(self):
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", 8000))
        self.debug = os.getenv("DEBUG", "true").lower() == "true"

        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")

        self.admin_url = os.getenv("ADMIN_URL", "http://localhost:8031")
        self.api_key = os.getenv("API_KEY", "a0b5441108f85e0e61d7f63ae3ae310dd06615bf6703154949a075d07963e9de")

        BASE_DIR = Path(__file__).resolve()
        for _ in range(6):
            if BASE_DIR.parent == BASE_DIR:
                break
            BASE_DIR = BASE_DIR.parent
        DB_PATH = BASE_DIR / "db" / "holder.db"
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        self.database_url = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

settings = Settings()
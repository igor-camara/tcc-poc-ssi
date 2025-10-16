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
        self.api_key = os.getenv("API_KEY", "mysecretapikey")

        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "myjwtsecretkey")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

        BASE_DIR = Path(__file__).resolve().parents[6]
        DB_PATH = BASE_DIR / "db" / "holder.db"
        
        self.database_url = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

settings = Settings()
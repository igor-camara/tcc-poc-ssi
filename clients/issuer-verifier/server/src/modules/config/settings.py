from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

class Settings:
    def __init__(self):
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", 8002))
        self.debug = os.getenv("DEBUG", "true").lower() == "true"

        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")

        self.admin_url = os.getenv("ADMIN_URL", "http://localhost:8051")
        self.api_key = os.getenv("API_KEY", "1e2ffb118cc0c8317df5190dd079b9380ceb0edc98bd0fb48c8f2dcba733daca")

        self.governance_url = os.getenv("GOVERNANCE_URL", "http://localhost:8003")
        self._governance_api_key = os.getenv("GOVERNANCE_API_KEY", "")

        BASE_DIR = Path(__file__).resolve()
        for _ in range(6):
            if BASE_DIR.parent == BASE_DIR:
                break
            BASE_DIR = BASE_DIR.parent
        DB_PATH = BASE_DIR / "db" / "verifier.db"
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        self.database_url = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

        self.company_name = os.getenv("COMPANY_NAME", "Verificador SSI")

    @property
    def governance_api_key(self) -> str:
        return os.environ.get("GOVERNANCE_API_KEY", self._governance_api_key)

settings = Settings()
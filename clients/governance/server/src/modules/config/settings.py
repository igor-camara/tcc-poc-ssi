from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import os
import logging

dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    try:
        parents = Path(__file__).resolve().parents
        repo_root = parents[3] if len(parents) > 3 else parents[-1]
        env_file = repo_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        else:
            logging.getLogger(__name__).warning(".env file not found; continuing without loading environment from file.")
    except Exception:
        logging.getLogger(__name__).exception("Failed to locate .env file (continuing without it)")

class Settings:
    def __init__(self):
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", 8003))
        self.debug = os.getenv("DEBUG", "true").lower() == "true"

        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")

        self.admin_url = os.getenv("ADMIN_URL", "http://localhost:8021")
        self.api_key = os.getenv("API_KEY", "ffbe0d09b05b46b442a82199206a8c9df97e513c06f05dd85075003430221fc6")

        self.company_name = os.getenv("COMPANY_NAME", "Governance")

        self.mongo_host = os.getenv("MONGODB_HOST", "localhost")
        self.mongo_port = int(os.getenv("MONGODB_PORT", 27017))
        self.mongo_username = os.getenv("MONGODB_USERNAME", "admin")
        self.mongo_password = os.getenv("MONGODB_PASSWORD", "admin123")
        self.mongo_database_name = os.getenv("MONGODB_DATABASE", "governance")

settings = Settings()
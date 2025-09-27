from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    def __init__(self):
        self.host = os.getenv("HOST", "127.0.0.1")
        self.port = int(os.getenv("PORT", 8000))
        self.debug = os.getenv("DEBUG", "true").lower() == "true"

        self.admin_url = os.getenv("ADMIN_URL", "http://localhost:8021")
        self.api_key = os.getenv("API_KEY", "mysecretapikey")

        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "myjwtsecretkey")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

settings = Settings()

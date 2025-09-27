from pydantic import BaseModel

class AuthUser(BaseModel):
    user_name: str
    user_surname: str
    user_email: str
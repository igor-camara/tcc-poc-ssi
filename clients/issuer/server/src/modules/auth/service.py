import modules.user.service as user_service
from modules.auth.schema import AuthRegisterRequest, AuthLoginRequest
from modules.utils.token import create_access_token
from modules.utils.password import verify_password

def register_user(credentials: AuthRegisterRequest) -> tuple[dict, dict] | str:
    existing_user = user_service.get_user_by_email(credentials.email)
    if existing_user:
        return "USER_ALREADY_EXISTS"

    user = user_service.create_user(
        name=credentials.first_name + " " + credentials.last_name,
        email=credentials.email,
        password=credentials.password
    )

    response = { "user_name": user.first_name, "user_surname": user.last_name, "user_email": user.email }

    return response

def login_user(credentials: AuthLoginRequest) -> tuple[dict, dict] | str:
    user = user_service.get_user_by_email(credentials.email)

    if not user:
        return "USER_NOT_FOUND"

    if not verify_password(credentials.password, user.password_hash):
        return "INVALID_PASSWORD"

    response = { "user_name": user.first_name, "user_surname": user.last_name, "user_email": user.email }

    return response
import modules.user.service as user_service
import modules.invitation.service as agent_service
from modules.auth.schema import AuthRegisterRequest, AuthLoginRequest
from modules.utils.token import create_access_token
from modules.utils.password import verify_password

async def register_user(credentials: AuthRegisterRequest) -> tuple[dict, dict] | str:
    existing_user = user_service.get_user_by_email(credentials.email)
    if existing_user:
        return "USER_ALREADY_EXISTS"

    try:
        did_info = await agent_service.create_did(credentials.email)
    except Exception as e:
        return "DID_CREATION_FAILED"

    user = user_service.create_user(
        name=credentials.first_name + " " + credentials.last_name,
        email=credentials.email,
        password=credentials.password,
        did=did_info['did'],
        verkey=did_info['verkey']
    )

    access_token = create_access_token(data={"sub": user.id})

    response = { "user_name": user.first_name, "user_surname": user.last_name, "user_email": user.email }

    auth_headers = { "token": access_token, "did": user.did, "verkey": user.verkey }

    return response, auth_headers

def login_user(credentials: AuthLoginRequest) -> tuple[dict, dict] | str:
    user = user_service.get_user_by_email(credentials.email)

    if not user:
        return "USER_NOT_FOUND"

    if not verify_password(credentials.password, user.password_hash):
        return "INVALID_PASSWORD"

    access_token = create_access_token(data={"sub": user.id})

    response = { "user_name": user.first_name, "user_surname": user.last_name, "user_email": user.email }

    auth_headers = { "Authorization": access_token, "x-did": user.did, "x-verkey": user.verkey }

    return response, auth_headers
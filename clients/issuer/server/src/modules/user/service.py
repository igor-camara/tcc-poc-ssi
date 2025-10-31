from modules.user.schema import User

def get_user_by_email(email: str) -> User | None:
    return User.find_by_email(email)

def get_user_by_id(user_id: str) -> User | None:
    return User.find_by_id(user_id)

def create_user(name: str, email: str, password: str) -> User:
    name_parts = name.split(' ', 1)
    first_name = name_parts[0] if name_parts else ''
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password
    )
    user.save()
    return user

def authenticate_user(email: str, password: str) -> User | None:
    """Authenticate user with email and password"""
    user = get_user_by_email(email)
    if user and user.check_password(password):
        return user
    return None
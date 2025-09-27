from api.schemas.user import User

def get_user_by_email(email):
    return User.find_by_email(email)

def create_user(name, email, password, did, verkey):  
    user = User(
        email=email,
        password=password,
        first_name=name.split(" ")[0],
        last_name=name.split(" ")[-1] if len(name.split(" ")) > 1 else "",
        did=did,
        verkey=verkey
    )
    user.save()
    return user

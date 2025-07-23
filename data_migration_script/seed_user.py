import constants
from database import get_session
from models import LoginCred


def saveUser(user_name, password, provider):
    session = get_session()

    print(user_name, password, provider)

    existing_user = session.query(LoginCred).filter(
        LoginCred.username == user_name,
        LoginCred.provider == provider
    ).first()

    if existing_user:
        return False, "User already exists."
    else:
        # Add new user if not found
        new_user = LoginCred(
            username=user_name,
            password=password,
            provider=constants.Provider(provider)
        )
        session.add(new_user)
        session.commit()  # Commit the transaction
        session.refresh(new_user)  # Refresh to get auto-generated ID, etc.

        return True, "User saved successfully."


if __name__ == '__main__':
    provider = input(f'provider default values : {constants.Provider._member_names_}').upper()

    provider = constants.Provider(provider)
    print(provider)
    user_name = input('user_name')
    password = input('password')

    print(saveUser(user_name, password, provider))

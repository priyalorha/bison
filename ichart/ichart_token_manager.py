from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pytz

import constants
from Errors.broker_auth_error import BrokerAuthError
from Errors.user_not_found import UserNotFoundError
from models.orm.login_cred import LoginCred
from models.orm.ichart_session_token import IChartSessionToken


class IChartTokenManager:

    def __init__(self, session: Session):

        self.session = session
        self.token_expiry_duration = timedelta(hours=23)

    def get_token_for_user(self, user_id: int, force_new: bool = False) -> str:

        user = self.session.query(LoginCred).filter(LoginCred.id == user_id).first()

        if not user:
            raise UserNotFoundError(f"LoginCred with ID {user_id} not found.")

        if user.provider != constants.Provider.ICHART:
            raise ValueError(f"User ID {user_id} is not an ICHART user. Provider is {user.provider.name}.")

        token_obj = self.session.query(IChartSessionToken).filter(
            IChartSessionToken.login_cred_id == user.id
        ).first()

        try:
            if force_new:
                print(f"Force generating new token for user '{user.username}'...")
                return self._generate_and_save_new_token(user, token_obj)

            elif token_obj and self._is_token_expired(token_obj):
                print(f"Token for user '{user.username}' is expired. Re-authenticating...")
                return self._generate_and_save_new_token(user, token_obj)

            elif not token_obj:
                print(f"No token found for user '{user.username}'. Authenticating and creating new token...")
                return self._generate_and_save_new_token(user, None)  # Pass None to indicate no existing token

            else:
                # Token exists and is not expired, and force_new is False
                print(f"Valid token found for user '{user.username}'.")
                return token_obj.token

        except BrokerAuthError as e:
            self.session.rollback()  # Rollback any pending changes if authentication failed
            raise BrokerAuthError(f"Authentication failed for user '{user.username}': {e}")
        except Exception as e:
            self.session.rollback()  # Rollback for any other unexpected errors
            raise Exception(f"An unexpected error occurred while processing token for user '{user.username}': {e}")

    def _is_token_expired(self, token_obj: IChartSessionToken) -> bool:

        if not token_obj or not token_obj.generated_at:
            return True
        generated_at_aware = constants.KOLKATA_TZ.localize(token_obj.generated_at)

        current_time_aware = datetime.now(constants.KOLKATA_TZ)

        return (current_time_aware - generated_at_aware) > self.token_expiry_duration

    def _generate_and_save_new_token(self, user: LoginCred, existing_token_obj: IChartSessionToken = None) -> str:

        auth_code = IChartAuthorization(user).authenticate()

        if existing_token_obj:
            existing_token_obj.token = auth_code
            existing_token_obj.generated_at = datetime.now(constants.KOLKATA_TZ).replace(
                tzinfo=None)
            self.session.add(existing_token_obj)
            self.session.commit()
            self.session.refresh(existing_token_obj)
            return existing_token_obj.token
        else:
            # Create new token
            new_token_obj = IChartSessionToken(
                token=auth_code,
                generated_at=datetime.now(constants.KOLKATA_TZ).replace(tzinfo=None),  # Store naive
                login_cred_id=user.id
            )
            self.session.add(new_token_obj)
            self.session.commit()
            self.session.refresh(new_token_obj)
            return new_token_obj.token

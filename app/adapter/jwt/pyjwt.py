from typing import Optional, List
import datetime
import jwt

from app.adapter.jwt import model
from app import lib as lib_models
from app.adapter.log import model as log_model



class AuthPyJWT(model.AuthJWT):
    def __init__(self, settings: lib_models.settings.Setting, log: log_model.LogAdapter) -> None:
        super().__init__(settings=settings, log=log)

    def encode(self, user: model.AuthUser, aud: List[str], expiration: Optional[datetime.timedelta] = None) -> model.EncodedJWT:
        current_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        if not expiration:
            expiration = current_datetime + self.settings.expiration_access_token

        to_access_token = model.JWTData(
            user=user,
            aud=aud,
            gen=current_datetime,
            exp=expiration,
        )
        to_refresh_token = model.RefreshAuthUser(
            id=user.id,
            gen=current_datetime,
            exp=expiration,
        )

        if not self.settings.auth_access_token_secret:
            raise ValueError(f"Require a auth_access_token_secret valid")
        if not self.settings.auth_refresh_token_secret:
            raise ValueError(f"Require a auth_refresh_token_secret valid")

        access_token = jwt.encode(
            payload=to_access_token.dict(), 
            key=self.settings.auth_access_token_secret, 
            algorithm="HS256",
        )
        refresh_token = jwt.encode(
            payload=to_refresh_token.dict(), 
            key=self.settings.auth_refresh_token_secret, 
            algorithm="HS256"
        )

        return model.EncodedJWT(
            type=self.settings.auth_type,
            access_token=access_token,
            refresh_token=refresh_token,
            generation=current_datetime,
            expiration=expiration,
        )

    def check_and_decode(self, token: str, allowed_aud: List[str]) -> model.StatusCheckJWT:
        status = True
        message = "Active Token"
        data = None
        type = model.StatusType.OK

        try:
            decoded = jwt.decode(
                token, 
                self.settings.auth_access_token_secret, 
                audience=allowed_aud, 
                algorithm="HS256"
            )
            data = model.JWTData(**decoded)
        except jwt.exceptions.InvalidAudienceError:
            status = False
            message = "You don't have permissions for this resource"
            type = model.StatusType.NOT_PERMISSIONS
        except jwt.exceptions.ExpiredSignatureError:
            status = False
            message = "Not valid token, expired signature"
            type = model.StatusType.EXPIRED
        except jwt.exceptions.DecodeError:
            status = False
            message = "Not Complete Information in Token"
            type = model.StatusType.NOT_COMPLETE
        except Exception as exc:
            # General Error
            self.log.error(f"JWT Error - {exc}")
            status = False
            message = "Not Authorized"
            type = model.StatusType.NOT_AUTHORIZED
            
        return model.StatusCheckJWT(
            type=type,
            status=status,
            message=message,
            data=data,
        )

    def check_refresh_and_decode(self, token: str) -> model.StatusCheckJWT:
        status = True
        message = "Active Refresh Token"
        data = None
        type = model.StatusType.OK

        try:
            decoded = jwt.decode(
                token, 
                self.settings.auth_refresh_token_secret,
                algorithms="HS256",
            )
            data = model.RefreshAuthUser(**decoded)
        except jwt.exceptions.ExpiredSignatureError:
            status = False
            message = "Not valid token, expired signature"
            type = model.StatusType.EXPIRED
        except jwt.exceptions.DecodeError:
            status = False
            message = "Not Complete Information in Token"
            type = model.StatusType.NOT_COMPLETE
        except Exception as exc:
            # General Error
            self.log.error(f"JWT Error - {exc}")
            status = False
            message = "Not Authorized"
            type = model.StatusType.NOT_AUTHORIZED

        return model.StatusCheckJWT(
            type=type,
            status=status,
            message=message,
            data=data,
        )
    
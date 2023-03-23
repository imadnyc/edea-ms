import os
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, Header, HTTPException, status
from jwt import InvalidTokenError, MissingRequiredClaimError, PyJWKClient
from sqlalchemy import select

from app.db import async_session
from app.db.models import User

jwks_client = PyJWKClient(
    os.getenv("JWKS_URL", "http://test/.well-known/jwks.json"), cache_keys=True
)


async def get_current_user(
    token: str | None = Cookie(default=None),
    authorization: str | None = Header(default=None),
    webauth_user: str | None = Header(default=None, alias="X-Webauth-User"),
) -> User:
    # we could add some different methods for getting the user here
    # e.g. if a frontend proxy does validation already, we could directly trust
    # some headers with the information we need.

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    claims_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication token does not contain groups claim",
    )

    groups: list[str] = []

    # get the user information either from headers or a token
    if webauth_user:
        username = webauth_user
    else:
        if token is None and authorization is None:
            raise credentials_exception

        # use token or authentication header, strip off "Bearer " part for header
        p_tok = token or authorization.split(" ")[-1] if authorization else ""

        try:
            signing_key = jwks_client.get_signing_key_from_jwt(p_tok)
            payload = jwt.decode(
                p_tok,
                signing_key.key,
                algorithms=["HS256", "ES256", "ES256K", "EdDSA"],
                options={"require": ["exp", "iss", "sub", "groups"]},
            )
            # sub and groups are required for decoding, should always be some
            username = payload.get("sub") or ""
            groups = payload.get("groups") or []
        except MissingRequiredClaimError as e:
            raise claims_exception from e
        except InvalidTokenError as e:
            raise credentials_exception from e

    # get the user info or create a new one if it's the first time they access the server
    async with async_session() as session:
        u = (
            await session.scalars(select(User).where(User.subject == username))
        ).one_or_none()

        # create a new user if we don't have one with the subject name
        if u is None:
            u = User(
                subject=username,
                preferred_username="",
                groups=groups,
                disabled=False,
            )
            session.add(u)
            await session.commit()

        return u


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# annotated dependency for the routers
CurrentUser = Annotated[User, Depends(get_current_active_user)]

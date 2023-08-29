import os
from contextvars import ContextVar
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from jwt import InvalidTokenError, MissingRequiredClaimError, PyJWKClient
from sqlalchemy import select
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from app.db import async_session
from app.db.models import User

REQUEST_USER_CTX_KEY = "request_user"

_request_user_ctx_var: ContextVar[User | None] = ContextVar(
    REQUEST_USER_CTX_KEY, default=None
)

jwks_client = PyJWKClient(
    os.getenv("JWKS_URL", "http://test/.well-known/jwks.json"), cache_keys=True
)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
claims_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication token does not contain groups claim",
)


async def get_current_user(
    token: str | None = None,
    authorization: str | None = None,
    x_webauth_user: str | None = None,
    x_webauth_groups: list[str] | None = None,
    x_webauth_roles: list[str] | None = None,
) -> User | None:
    """
    get_current_user returns the currently logged in user or creates it if it's the first
    time we see them. it can take a JSON Web Token (JWT) as a cookie or an Authorization header.
    Alternatively, it also accepts X-Webauth-{User,Groups,Roles} headers which specify the user
    details further.
    """

    groups: list[str] = []
    roles: list[str] = []

    # get the user information either from headers or a token
    if x_webauth_user:
        username = x_webauth_user
        groups = x_webauth_groups or []
        roles = x_webauth_roles or []

        # handle multiple field values in a single header according to RFC9110, section 5.3.
        if len(groups) == 1 and "," in groups[0]:
            groups = groups[0].split(",")
        if len(roles) == 1 and "," in roles[0]:
            roles = roles[0].split(",")
    else:
        if token is None and authorization is None:
            return None

        # use token or authentication header, strip off "Bearer " part for header
        p_tok = token or authorization.split(" ")[-1] if authorization else ""

        groups, roles, username = _parse_jwt(p_tok)

    # get the user info or create a new one if it's the first time they access the server
    async with async_session() as session:
        u = (
            await session.scalars(select(User).where(User.subject == username))
        ).one_or_none()

        # create a new user if we don't have one with the subject name
        if u is None:
            u = User(
                subject=username,
                displayname="",
                groups=groups,
                roles=roles,
                disabled=False,
            )
            session.add(u)
            await session.commit()
        elif (
            u.groups != groups or u.roles != roles
        ):  # or update if groups or roles changed
            u.groups = groups
            u.roles = roles
            session.add(u)
            await session.commit()

        return u


def _parse_jwt(token: str) -> tuple[list[str], list[str], str]:
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["HS256", "ES256", "ES256K", "EdDSA"],
            options={"require": ["exp", "iss", "sub", "groups"]},
        )
        # sub and groups are required for decoding, should always be some
        username = payload.get("sub") or ""

        # groups and roles are registered claims according to RFC 9068
        groups = payload.get("groups") or []
        roles = payload.get("roles") or []
    except MissingRequiredClaimError as e:
        raise claims_exception from e
    except InvalidTokenError as e:
        raise credentials_exception from e
    return groups, roles, username


class AuthenticationMiddleware:
    """
    AuthenticationMiddleware provides the default way of extracting user information
    from a request. It supports JWTs as cookies or headers or directly trusted headers
    with the necessary information.

    For different authentication needs, another middleware can be used, it's only necessary
    that the _request_user_ctx_var gets filled with a user object.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        request = Request(scope)

        authorization = request.headers.get("authorization")
        x_webauth_user = request.headers.get("x-webauth-user")
        x_webauth_groups = request.headers.getlist("x-webauth-groups")
        x_webauth_roles = request.headers.getlist("x-webauth-roles")
        token = request.cookies.get("token")

        u = await get_current_user(
            token, authorization, x_webauth_user, x_webauth_groups, x_webauth_roles
        )
        ctx_token = _request_user_ctx_var.set(u)

        await self.app(scope, receive, send)

        _request_user_ctx_var.reset(ctx_token)


def get_current_active_user() -> User:
    current_user = _request_user_ctx_var.get()

    if current_user is None:
        raise credentials_exception

    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


# annotated dependency for the routers
CurrentUser = Annotated[User, Depends(get_current_active_user)]

import jwt
from jose.exceptions import JWTError, ExpiredSignatureError

from fastapi import Request, HTTPException, status, Depends
from datetime import datetime, timezone

from app.api.v1.crud import get_user_by_id
from app.core.dependencies import get_database
from app.core.database import Database
from app.core.config import settings


def get_token(request: Request) -> str:
    """
    Извлекает JWT access-токен из cookie или заголовка Authorization.

    :param request: HTTP-запрос.
    :return: Строка access-токена.
    :raises HTTPException: Если токен отсутствует.
    """
    token = request.cookies.get("access_token")

    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token not found",
        )

    return token


async def get_current_user(
    token: str = Depends(get_token),
    db: Database = Depends(get_database),
):
    """
    Проверяет валидность JWT access-токена и возвращает данные пользователя.

    :param token: JWT-токен, полученный из cookie или заголовка Authorization.
    :param db: Экземпляр базы данных.
    :return: Данные пользователя.
    :raises HTTPException: Если токен невалидный, истек, либо пользователь не найден.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        if payload.get("token_type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        expire = payload.get("exp")
        if not expire or datetime.fromtimestamp(expire, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token has expired",
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token",
            )

        user = await get_user_by_id(db, int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return user
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )
from fastapi import APIRouter, HTTPException, status, Response, Depends, Request
from fastapi.responses import RedirectResponse
from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.users.dao import UsersDAO, LogDAO
from app.users.dependencies import get_current_user, get_current_admin_user
from app.users.models import User, Log
from app.users.schemas import SUserRegister, SUserAuth
from app.config import settings
import httpx
from datetime import datetime

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post("/register/")
async def register_user(user_data: SUserRegister) -> dict:
    user = await UsersDAO.find_one_or_none(email=user_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь уже существует'
        )
    user_dict = user_data.dict()
    user_dict['password'] = get_password_hash(user_data.password)
    await UsersDAO.add(**user_dict)
    return {'message': 'Вы успешно зарегистрированы!'}


@router.post("/login/")
async def auth_user(response: Response, user_data: SUserAuth):
    check = await authenticate_user(email=user_data.email, password=user_data.password)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)

    # Логирование входа
    await LogDAO.add(user_id=check.id)

    return {'access_token': access_token, 'refresh_token': None}


@router.get("/me/")
async def get_me(user_data: User = Depends(get_current_user)):
    return user_data


@router.post("/logout/")
async def logout_user(response: Response, user_data: User = Depends(get_current_user)):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}


@router.get("/all_users/")
async def get_all_users(user_data: User = Depends(get_current_admin_user)):
    return await UsersDAO.find_all()


YANDEX_AUTH_URL = "https://oauth.yandex.ru/authorize"
YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
YANDEX_USER_INFO_URL = "https://login.yandex.ru/info"


@router.get("/yandex/login/")
async def login_via_yandex():
    return RedirectResponse(
        f"{YANDEX_AUTH_URL}?response_type=code&client_id={settings.YANDEX_CLIENT_ID}"
    )


@router.get("/yandex/callback/")
async def yandex_callback(code: str, request: Request):
    async with httpx.AsyncClient() as client:
        # Получаем токен доступа
        token_response = await client.post(
            YANDEX_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.YANDEX_CLIENT_ID,
                "client_secret": settings.YANDEX_CLIENT_SECRET,
            },
        )
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не удалось получить токен доступа")

        # Получаем информацию о пользователе
        user_info_response = await client.get(
            YANDEX_USER_INFO_URL,
            headers={"Authorization": f"OAuth {access_token}"},
        )
        user_info = user_info_response.json()

        # Проверяем, есть ли пользователь в базе данных
        user = await UsersDAO.find_one_or_none(email=user_info.get("default_email"))
        if not user:
            # Создаем нового пользователя, если его нет
            user_data = {
                "email": user_info.get("default_email"),
                "first_name": user_info.get("first_name"),
                "last_name": user_info.get("last_name"),
                "password": get_password_hash("random_password"),  # Генерация случайного пароля
            }
            user = await UsersDAO.add(**user_data)

        # Создаем токен доступа для вашего приложения
        access_token = create_access_token({"sub": str(user.id)})
        response = RedirectResponse(url="/")
        response.set_cookie(key="users_access_token", value=access_token, httponly=True)

        # Логирование входа через Яндекс
        await LogDAO.add(user_id=user.id)

        return response

@router.get("/logs/")
async def get_login_history(user_data: User = Depends(get_current_user)):
    logs = await LogDAO.find_all(user_id=user_data.id)
    return logs

@router.post("/make_admin/")
async def make_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin_user)
):
    user_to_update = await UsersDAO.find_one_or_none_by_id(user_id)
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    await UsersDAO.update(filter_by={"id": user_id}, is_admin=True)
    return {"message": f"Пользователь {user_to_update.email} теперь администратор"}
from app.dao.base import BaseDAO
from app.users.models import User
from app.users.models import Log


class UsersDAO(BaseDAO):
    model = User


class LogDAO(BaseDAO):
    model = Log
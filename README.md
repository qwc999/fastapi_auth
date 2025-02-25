
Реализовано:
* Система авторизации
* Поддержка входа через яндекс
* Ролевая модель (админам доступен просмотр всех пользователей и выдача прав админа другим пользователям)
* Логирование входов в систему (таблица logs)
* Воркер, слушающий события rabbitmq, отправляет сообщения в [группу](https://t.me/+HcogbLRHBBhhYzM6) через телеграм бота

![image](https://github.com/user-attachments/assets/5335ee04-dec2-451b-afcc-396e598f6bfd)

Как запустить проект:
```
alembic revision --autogenerate -m "Migration"
alembic upgrade head     (миграции)

python app/worker.py
uvicorn app.main:app --reload
```

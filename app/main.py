from fastapi import FastAPI
from app.users.router import router as router_users

app = FastAPI()


@app.get("/")
def home_page():
    return {"message": "http://127.0.0.1:8000/docs/"}


app.include_router(router_users)

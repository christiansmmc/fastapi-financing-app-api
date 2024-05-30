from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routers import users, login, transactions, tags

app = FastAPI()

app.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
)
app.include_router(
    login.router,
    prefix="/login",
    tags=["login"],
)
app.include_router(
    transactions.router,
    prefix="/transactions",
    tags=["transactions"],
)
app.include_router(
    tags.router,
    prefix="/tags",
    tags=["tags"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "OK"}

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routers import user_routes, login_routes, transaction_routes, tags_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    user_routes.router,
    prefix="/users",
    tags=["users"],
)
app.include_router(
    login_routes.router,
    prefix="/login",
    tags=["login"],
)
app.include_router(
    transaction_routes.router,
    prefix="/transactions",
    tags=["transactions"],
)
app.include_router(
    tags_routes.router,
    prefix="/tags",
    tags=["tags"],
)


@app.get("/")
def read_root():
    return {"status": "OK"}

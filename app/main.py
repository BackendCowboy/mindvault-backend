# app/main.py
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from app.auth_routes import router as auth_router
from app.user_routes import router as user_router
from app.journal_routes import router as journal_router
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="MindVault API",
    version="1.0.0",
    description="Secure Journal & Auth API",
    openapi_tags=[
        {"name": "Auth",    "description": "Register & login"},
        {"name": "Users",   "description": "User profile"},
        {"name": "Journal", "description": "Journal entries & insights"},
    ],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "bearerAuth": {"type":"http","scheme":"bearer","bearerFormat":"JWT"}
    }
    for path in schema["paths"].values():
        for op in path.values():
            op.setdefault("security", [{"bearerAuth": []}])
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(journal_router)
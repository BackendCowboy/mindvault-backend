# main.py
from fastapi import FastAPI
from sqlmodel import SQLModel
from database import engine
from routes import router
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# Apply custom JWT security to Swagger docs
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="MindVault API",
        version="1.0.0",
        description="Secure Journal & Auth API",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"bearerAuth": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Register your router
app.include_router(router)
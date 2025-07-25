from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router
from app.routes.journal_routes import router as journal_router
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from app.limiter import limiter
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from app.routes.ai_routes import router as ai_router
from app.error_handlers import register_exception_handlers
from app.routes.health_routes import router as health_router


app = FastAPI(
    title="MindVault API",
    version="1.0.0",
    description="Secure Journal & Auth API",
    openapi_tags=[
        {"name": "Auth", "description": "Register & login"},
        {"name": "Users", "description": "User profile"},
        {"name": "Journal", "description": "Journal entries & insights"},
    ],
)

register_exception_handlers(app)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )


# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ Secure custom OpenAPI with bearer token support
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
        "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path in schema["paths"].values():
        for op in path.values():
            op.setdefault("security", [{"bearerAuth": []}])
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi


# ✅ Add routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(journal_router)
app.add_middleware(SlowAPIMiddleware)
app.state.limiter = limiter
app.include_router(ai_router)
app.include_router(health_router)

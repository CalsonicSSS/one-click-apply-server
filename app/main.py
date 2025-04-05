from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from .routes.suggestion_generation import router as suggestion_generation_router
from .routes.payments import router as payments_router
from .routes.users import router as users_router
from .db.database import init_db, close_db_connection
from contextlib import asynccontextmanager


config_settings = get_settings()
print(config_settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await init_db()
    yield
    # Shutdown logic
    await close_db_connection()


app = FastAPI(title=config_settings.PROJECT_NAME, version=config_settings.VERSION, lifespan=lifespan)

# Middleware is applied globally to all requests that reach the FastAPI application (Dependencies are different, they are applied to specific endpoint)
app.add_middleware(
    CORSMiddleware,
    # these are 4 main checks setup for CORS, they are all part of the same middleware here.
    allow_origins=config_settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(suggestion_generation_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    print("health check reached")
    return {"status": "healthy"}

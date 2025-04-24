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
# You can add multiple middleware for different purposes
# Middleware runs in the order it's added. If you add MiddlewareA then MiddlewareB, A processes the request first.

# "add_middleware": A method to register middleware on your FastAPI app.
# First argument is the middleware class (not an instance!), followed by its configuration (VERY IMPORTANT PATTERN IN fastapi).
# Named arguments (allow_origins, allow_methods, etc.): These are specific to CORSMiddleware and define its behavior. Other middleware types (e.g., authentication) would take different arguments.
app.add_middleware(
    # CORSMiddleware A pre-built class provided by FastAPI It handles all CORS-related headers automatically.
    CORSMiddleware,
    # these are 4 main checks setup for CORS related middleware, they are all part of the SAME middleware here.
    allow_origins=config_settings.ALLOWED_ORIGINS,
    allow_credentials=True,  # Allows cookies/auth headers (e.g., for JWT).
    allow_methods=["*"],  # HTTP methods permitted (e.g., ["GET", "POST"]).
    allow_headers=["*"],
)

# To add other middleware, you'd call app.add_middleware() again with a different class.

app.include_router(suggestion_generation_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    print("health check reached")
    return {"status": "healthy"}

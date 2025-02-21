from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

config_settings = get_settings()
print(config_settings)

app = FastAPI(
    title=config_settings.PROJECT_NAME,
    version=config_settings.VERSION,
)

# Middleware is applied globally to all requests that reach the FastAPI application (Dependencies are different, they are applied to specific endpoint)
app.add_middleware(
    CORSMiddleware,
    # these are 4 main checks setup for CORS, they are all part of the same middleware here.
    allow_origins=config_settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# We'll add routers here later


@app.get("/health")
async def health_check():
    print("health check reached")
    return {"status": "healthy"}

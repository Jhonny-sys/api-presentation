from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.supabase import get_supabase_client
from app.middleware.jwt_auth import JWTAuthMiddleware
from app.routers import auth, flaticon, i18n, portfolio, uploads
from app.services.token_cleanup_service import TokenCleanupService


@asynccontextmanager
async def lifespan(app: FastAPI):
    TokenCleanupService(get_supabase_client()).purge_if_due(force=True)
    yield


app = FastAPI(
    title="API Presentation",
    description="Backend del catálogo profesional de Jhonny",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(JWTAuthMiddleware)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(i18n.router, prefix=settings.api_prefix)
app.include_router(uploads.router, prefix=settings.api_prefix)
app.include_router(portfolio.router, prefix=settings.api_prefix)
app.include_router(flaticon.router, prefix=settings.api_prefix)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

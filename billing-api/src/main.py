from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from sqlalchemy import Table, MetaData
from sqlalchemy.ext.asyncio import create_async_engine

from core.config import settings
from db import postgres
from models import tariff
from api.v1 import tariffs
from api import healthcheck



@asynccontextmanager
async def lifespan(app: FastAPI):
    postgres.engine = create_async_engine(settings.dsn, future=True)
    yield
    postgres.engine = None


app = FastAPI(
    title='BillingService',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


app.include_router(healthcheck.router, prefix="/api/v1")
app.include_router(tariffs.router, prefix="/api/v1/tariffs", tags=['tariff'])

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import create_async_engine

from core.config import settings
from core.exceptions import BaseErrorWithContent
from db import postgres
from api.v1 import tariffs
from api.v1 import subscription
from api import healthcheck
from tasks import auto_pay


@asynccontextmanager
async def lifespan(app: FastAPI):
    postgres.engine = create_async_engine(settings.dsn, future=True)
    auto_pay.delay()
    yield
    postgres.engine = None


app = FastAPI(
    title='BillingService',
    docs_url='/billing-api/openapi',
    openapi_url='/billing-api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


@app.exception_handler(BaseErrorWithContent)
async def project_error_handler(request: Request, exc: BaseErrorWithContent):
    return ORJSONResponse(
        status_code=exc.status_code,
        content=exc.content,
    )

app.include_router(healthcheck.router, prefix="/billing-api/v1")
app.include_router(tariffs.router, prefix="/billing-api/v1", tags=['tariffs'])
app.include_router(subscription.router, prefix="/billing-api/v1", tags=['subscription'])

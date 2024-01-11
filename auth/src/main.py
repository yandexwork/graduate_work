from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

from src.core.config import settings
from src.core.exceptions import CustomException
from src.services.users import create_admin
from src.limiter import limiter
from src.api.v1 import users
from src.api.v1 import auth
from src.api.v1 import roles
from src.core.config import auth_jwt_settings


def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider(
        resource=Resource.create({SERVICE_NAME: "auth.api"})
    ))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.jaeger_agent_host_name,
                agent_port=settings.jaeger_agent_port
            )
        )
    )
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


configure_tracer()


app = FastAPI(
    title='AuthService',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse
)

FastAPIInstrumentor.instrument_app(app)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SessionMiddleware, secret_key=auth_jwt_settings.authjwt_secret_key)


@app.middleware('http')
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'})
    return response


@app.exception_handler(CustomException)
async def uvicorn_exception_handler(request: Request, exc: CustomException):
    return ORJSONResponse(status_code=exc.status_code, content={'message': exc.message})


@app.on_event("startup")
async def startup() -> None:
    await create_admin()


app.include_router(users.router, prefix='/api/v1/users', tags=['users'])
app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])
app.include_router(roles.router, prefix='/api/v1/roles', tags=['roles'])

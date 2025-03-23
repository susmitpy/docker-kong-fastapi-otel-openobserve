from fastapi import FastAPI, Request
from obs_utils import setup_tracer_and_logger
from opentelemetry.trace import Tracer
from logging import Logger
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import ulid

def create_app(service_name: str) -> tuple[FastAPI, Tracer, Logger]:
    app = FastAPI()

    app_instance_id = str(ulid.ULID())

    @app.middleware("http")
    async def add_app_instance_id_header(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-App-Instance-ID"] = app_instance_id
        return response
    
    tracer_provider, logger = setup_tracer_and_logger(service_name)

    # FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)
    
    tracer = tracer_provider.get_tracer(service_name)

    print(f"{service_name} service is running, instance id: {app_instance_id}")
    return app, tracer, logger
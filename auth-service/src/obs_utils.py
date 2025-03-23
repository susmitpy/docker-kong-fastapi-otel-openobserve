import datetime
import logging
import os
from fastapi import Request
from opentelemetry._logs import set_logger_provider

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry import trace

TRACES_ENDPOINT = os.environ.get("TRACES_ENDPOINT")
LOGS_ENDPOINT = os.environ.get("LOGS_ENDPOINT")

class TraceEnricher(logging.Filter):
    """Filter that enriches log records with trace information."""
    
    def filter(self, record):
        span = trace.get_current_span()
        span_context = span.get_span_context()
        
        # Add trace and span IDs
        if span_context.is_valid:
            record.trace_id = f"{span_context.trace_id:032x}"
            record.span_id = f"{span_context.span_id:016x}"
        else:
            record.trace_id = "N/A"
            record.span_id = "N/A"
            
        # Add request attributes from span if they exist
        record.kong_request_id = "N/A"
        record.auth_user = "N/A"
        
        # Try to get attributes from the current span
        if hasattr(span, "attributes"):
            record.kong_request_id = span.attributes.get("kong_request_id", "N/A")
            record.auth_user = span.attributes.get("auth_user", "N/A")
            
        return True  # Always return True to keep the record

class ISTFormatter(logging.Formatter):
    """Formatter that formats time in IST timezone."""
    
    def formatTime(self, record, datefmt=None):
        """Format time in IST timezone for consistency in Docker containers"""
        # Get UTC time and add 5 hours and 30 minutes for IST
        utc_time = datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc)
        ist_time = utc_time + datetime.timedelta(hours=5, minutes=30)
        
        if datefmt:
            return ist_time.strftime(datefmt)
        else:
            return ist_time.strftime("%Y-%m-%d %H:%M:%S") + f".{int(record.msecs):03d}"

def setup_tracer_and_logger(service_name: str) -> tuple[TracerProvider, logging.Logger]:
    resource = Resource({"service.name": service_name})
    
    # Setup tracer
    tracer_provider = TracerProvider(resource=resource)

    if TRACES_ENDPOINT is None:
        tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    else:
        otlp_exporter = OTLPSpanExporter(endpoint=TRACES_ENDPOINT)
        tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Set the tracer provider as the global default
    trace.set_tracer_provider(tracer_provider)

    logger_level = getattr(logging, os.environ.get("LOGGER_LEVEL", "INFO"))
    console_level = getattr(logging, os.environ.get("CONSOLE_LOG_LEVEL", "INFO")) 
    otel_level = getattr(logging, os.environ.get("OTEL_LOG_LEVEL", "INFO"))
    
    # Setup standard Python logger
    logger = logging.getLogger(service_name)
    logger.setLevel(logger_level)
    
    # Add the trace enricher filter to the logger
    trace_enricher = TraceEnricher()
    logger.addFilter(trace_enricher)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    # Use the IST time formatter for console output
    formatter = ISTFormatter('%(asctime)s - %(name)s - [trace_id=%(trace_id)s span_id=%(span_id)s request_id=%(kong_request_id)s user=%(auth_user)s] - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Setup OpenTelemetry logging if endpoint is provided
    if LOGS_ENDPOINT is not None:
        logger_provider = LoggerProvider(resource)
        set_logger_provider(logger_provider)
        otlp_log_exporter = OTLPLogExporter(endpoint=LOGS_ENDPOINT)
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))
        otel_handler = LoggingHandler(level=otel_level, logger_provider=logger_provider)
        logger.addHandler(otel_handler)
        
    return tracer_provider, logger

def set_request_attributes(func):
    async def wrapper(request: Request):
        kong_request_id = request.headers.get('x-kong-request-id')
        auth_user = request.headers.get('auth-user-identifier')
        if auth_user or kong_request_id:
            span = trace.get_current_span()
            if auth_user:
                span.set_attribute("auth_user", auth_user)
            if kong_request_id:
                span.set_attribute("kong_request_id", kong_request_id)
        return await func(request)
    return wrapper
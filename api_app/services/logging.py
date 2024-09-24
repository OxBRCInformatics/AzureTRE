import logging
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider  # Import this to create your own TracerProvider
from azure.monitor.opentelemetry import configure_azure_monitor

from core.config import APPLICATIONINSIGHTS_CONNECTION_STRING, LOGGING_LEVEL

# Initialize TracerProvider before using it
tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)  # Set the global tracer provider

logger = logging.getLogger("azuretre_api")
tracer = trace.get_tracer("azuretre_api", tracer_provider=tracer_provider)  # Now pass the initialized tracer provider


def configure_loggers():
    UNWANTED_LOGGERS = [
        "azure.core.pipeline.policies.http_logging_policy",
        "azure.eventhub._eventprocessor.event_processor",
        "azure.identity.aio._credentials.managed_identity",
        "azure.identity.aio._credentials.environment",
        "azure.identity.aio._internal.get_token_mixin",
        "azure.identity.aio._internal.decorators",
        "azure.identity.aio._credentials.chained",
        "azure.identity",
        "msal.token_cache",
        # Remove these once the following PR is merged:
        # https://github.com/Azure/azure-sdk-for-python/pull/30832
        # Issue: https://github.com/microsoft/AzureTRE/issues/3766
        "azure.servicebus._pyamqp.aio._session_async"
    ]

    LOGGERS_FOR_ERRORS_ONLY = [
        "azure.monitor.opentelemetry.exporter.export._base",
        "azure.servicebus.aio._base_handler_async",
        "azure.servicebus._pyamqp.aio._cbs_async",
        "azure.servicebus._pyamqp.aio._client_async",
        "azure.servicebus._pyamqp.aio._connection_async",
        "azure.servicebus._pyamqp.aio._link_async",
        "azure.servicebus._pyamqp.aio._management_link_async",
        "opentelemetry.attributes",
        "uamqp",
        "uamqp.async_ops",
        "uamqp.async_ops.client_async",
        "uamqp.async_ops.connection_async",
        "uamqp.async_ops.session_async",
        "uamqp.authentication",
        "uamqp.authentication.cbs_auth_async",
        "uamqp.c_uamqp",
        "uamqp.client",
        "uamqp.connection",
        "uamqp.receiver",
        "uamqp.sender",
        "urllib3.connectionpool"
    ]

    for logger_name in LOGGERS_FOR_ERRORS_ONLY:
        logging.getLogger(logger_name).setLevel(logging.ERROR)

    for logger_name in UNWANTED_LOGGERS:
        logging.getLogger(logger_name).setLevel(logging.CRITICAL)


def initialize_logging() -> logging.Logger:

    configure_loggers()

    logging_level = logging.INFO

    if LOGGING_LEVEL == "INFO":
        logging_level = logging.INFO
    elif LOGGING_LEVEL == "DEBUG":
        logging_level = logging.DEBUG
    elif LOGGING_LEVEL == "WARNING":
        logging_level = logging.WARNING
    elif LOGGING_LEVEL == "ERROR":
        logging_level = logging.ERROR

    if APPLICATIONINSIGHTS_CONNECTION_STRING:
        configure_azure_monitor(
            # connection_string=APPLICATIONINSIGHTS_CONNECTION_STRING,
            logger_name="azuretre_api",  # Set the logger name here
            instrumentation_options={
                "azure_sdk": {"enabled": False},  # Disable azure_sdk tracing
                "flask": {"enabled": False},      # Disable flask tracing
                "django": {"enabled": False},     # Disable django tracing
                "fastapi": {"enabled": True},     # Enable fastapi tracing
                "psycopg2": {"enabled": False},   # Disable psycopg2 tracing
            },
            tracer_provider=tracer_provider  # Pass correct tracer provider
        )

    LoggingInstrumentor().instrument(
        set_logging_format=True,
        log_level=logging_level,
        tracer_provider=tracer_provider  # Pass the initialized tracer provider here too
    )

    logger.info("Logging initialized with level: %s", LOGGING_LEVEL)

    return logger

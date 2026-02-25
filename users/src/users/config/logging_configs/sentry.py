import logging

from sentry_sdk.integrations.logging import LoggingIntegration

sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)

sentry_config = {
    "dsn": "http://c02ab681e9edfcb53c016255750b41ac@localhost:9000/2",
    "integrations": [sentry_logging],
    "send_default_pii": True,
}

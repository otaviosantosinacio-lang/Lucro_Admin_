import logging

from lucro_admin.infra.logging.contexto import correlation_id


class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # noqa: PLR6301
        record.correlation_id = correlation_id.get()
        return True

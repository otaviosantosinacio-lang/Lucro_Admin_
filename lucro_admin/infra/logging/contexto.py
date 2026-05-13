from contextvars import ContextVar
import uuid

correlation_id: ContextVar[str] = ContextVar('correlation_id', default='-')


def generate_correlation_id() -> str:
    return str(uuid.uuid4()).replace('-', '')[:12]

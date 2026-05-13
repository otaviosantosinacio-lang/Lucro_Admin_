from typing import Any

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = BASE_DIR / 'logs'

Logging_Config: dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'correlation_id': {'()': 'infra.logging.filters.CorrelationIdFilter'}
    },
    'formatters': {
        'error_file': {
            'format': '%(levelname)s | %(name)s | %(asctime)s | %(message)s | %(filename)s | %(lineno)d'
        },
        'file': {
            'format': '%(levelname)s | cid= %(correlation_id)s | %(name)s | %(asctime)s | %(message)s | %(filename)s | %(lineno)d'
        },
        'console': {'format': '%(message)s', 'datefmt': '[%X]'},
    },
    'handlers': {
        'errors_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'error_file',
            'filename': str(LOG_DIR / 'errors.log'),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 10,
            'encoding': 'utf-8',
        },
        'console': {
            '()': 'rich.logging.RichHandler',
            'level': 'INFO',
            'formatter': 'console',
            'rich_tracebacks': True,
            'tracebacks_show_locals': False,
            'show_time': True,
            'show_level': True,
            'omit_repeated_times': False,
            'markup': False,
            'enable_link_path': False,
            'show_path': False,
        },
        'main_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filters': ['correlation_id'],
            'formatter': 'file',
            'filename': str(LOG_DIR / 'main.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5mb 524880
            'backupCount': 5,
            'encoding': 'utf-8',
        },
        'adapters_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filters': ['correlation_id'],
            'formatter': 'file',
            'filename': str(LOG_DIR / 'adapters.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5mb 524880
            'backupCount': 5,
            'encoding': 'utf-8',
        },
        'services_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filters': ['correlation_id'],
            'formatter': 'file',
            'filename': str(LOG_DIR / 'services.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5mb 524880
            'backupCount': 5,
            'encoding': 'utf-8',
        },
        'infra_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filters': ['correlation_id'],
            'formatter': 'file',
            'filename': str(LOG_DIR / 'infra.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5mb 524880
            'backupCount': 5,
            'encoding': 'utf-8',
        },
        'core_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filters': ['correlation_id'],
            'formatter': 'file',
            'filename': str(LOG_DIR / 'core.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5mb 524880
            'backupCount': 5,
            'encoding': 'utf-8',
        },
        'utils_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filters': ['correlation_id'],
            'formatter': 'file',
            'filename': str(LOG_DIR / 'utils.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5mb 524880
            'backupCount': 5,
            'encoding': 'utf-8',
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'errors_file'],
        'propagate': True,
    },
    'loggers': {
        'lucroadmin.main': {
            'level': 'INFO',
            'handlers': ['main_file'],
            'propagate': True,
            'filters': ['correlation_id'],
        },
        'lucroadmin.adapters': {
            'level': 'INFO',
            'handlers': ['adapters_file'],
            'propagate': True,
            'filters': ['correlation_id'],
        },
        'lucroadmin.core': {
            'level': 'INFO',
            'handlers': ['core_file'],
            'propagate': True,
            'filters': ['correlation_id'],
        },
        'lucroadmin.infra': {
            'level': 'DEBUG',
            'handlers': ['infra_file'],
            'propagate': True,
            'filters': ['correlation_id'],
        },
        'lucroadmin.services': {
            'level': 'DEBUG',
            'handlers': ['services_file'],
            'propagate': True,
            'filters': ['correlation_id'],
        },
        'lucroadmin.utils': {
            'level': 'INFO',
            'handlers': ['utils_file'],
            'propagate': True,
            'filters': ['correlation_id'],
        },
    },
}

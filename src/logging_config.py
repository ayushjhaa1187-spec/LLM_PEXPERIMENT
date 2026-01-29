"""Logging and monitoring for Phase 1"""
import logging
import logging.config
import os

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': LOG_LEVEL,
            'formatter': 'default',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,
            'backupCount': 5
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': 'logs/error.log',
            'maxBytes': 10485760,
            'backupCount': 5
        }
    },
    'loggers': {
        'flask': {'handlers': ['console', 'file'], 'level': LOG_LEVEL},
        'sqlalchemy': {'handlers': ['console', 'file'], 'level': 'INFO'},
        'werkzeug': {'handlers': ['console'], 'level': 'INFO'},
    },
    'root': {
        'handlers': ['console', 'file', 'error_file'],
        'level': LOG_LEVEL,
    }
}

def configure_logging():
    os.makedirs('logs', exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {ENVIRONMENT}")
    return logger

class RequestLogger:
    @staticmethod
    def log_request(method, path, status_code, duration):
        logger = logging.getLogger(__name__)
        logger.info(f"Request: {method} {path} - Status: {status_code} - Duration: {duration}ms")
    
    @staticmethod
    def log_error(method, path, error, status_code):
        logger = logging.getLogger(__name__)
        logger.error(f"Error: {method} {path} - Status: {status_code} - {error}")

class MetricsCollector:
    def __init__(self):
        self.requests_count = 0
        self.errors_count = 0
        self.avg_response_time = 0
    
    def record_request(self, duration):
        self.requests_count += 1
        self.avg_response_time = (self.avg_response_time + duration) / 2
    
    def record_error(self):
        self.errors_count += 1
    
    def get_metrics(self):
        return {
            'requests': self.requests_count,
            'errors': self.errors_count,
            'avg_response_time': self.avg_response_time
        }

metrics = MetricsCollector()

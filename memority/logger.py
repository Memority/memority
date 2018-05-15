import json
import os
from logging import Handler, NOTSET, Formatter
from logging.config import DictConfigurator

from aiohttp import web

from bugtracking import raven_client
from settings import settings

__all__ = ['setup_logging']


class WSLogHandler(Handler):
    def __init__(self, *, level=NOTSET, ws: web.WebSocketResponse):
        super().__init__(level)
        self.ws = ws
        self.setFormatter(
            Formatter('[%(levelname)s] [%(asctime)s] [%(module)s] || %(message)s')
        )

    def emit(self, record):
        log_entry = self.format(record)
        data = json.dumps({
            "status": "action_needed",
            "details": "append_logs",
            "log_string": log_entry
        })
        self.ws._writer.send(data, binary=False, compress=None)


def rotating_log_file_handler(filename, formatter):
    return {
        'class': 'logging.handlers.RotatingFileHandler',
        'mode': 'a',
        'maxBytes': 1024 * 1024,
        'backupCount': 5,
        'formatter': formatter,
        'filename': os.path.join(settings.log_dir, f"{filename}.log"),
    }


_aiohttp_logger_config = {
    'handlers': ['stdout', 'aiohttp_log_file', 'sentry'],
    'level': 'INFO',
}


def setup_logging():
    configurator = DictConfigurator(
        {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'sentry': {
                    'format': '[%(asctime)s][%(levelname)s] %(name)s '
                              '%(filename)s:%(funcName)s:%(lineno)d | %(message)s',
                },
                'default': {
                    'format': '[%(levelname)s] [%(asctime)s] [%(module)s] || %(message)s'
                },
            },
            'handlers': {
                'stdout': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'default'
                },
                'sentry': {
                    'level': 'ERROR',
                    'class': 'raven.handlers.logging.SentryHandler',
                    'client': raven_client,
                    'formatter': 'sentry'
                },
                'aiohttp_log_file': rotating_log_file_handler("aiohttp", "default"),
                'memority_log_file': rotating_log_file_handler("memority", "default"),
                'monitoring_log_file': rotating_log_file_handler("monitoring", "default"),
            },
            'loggers': {
                'aiohttp.access': _aiohttp_logger_config,
                'aiohttp.client': _aiohttp_logger_config,
                'aiohttp.internal': _aiohttp_logger_config,
                'aiohttp.server': _aiohttp_logger_config,
                'aiohttp.web': _aiohttp_logger_config,
                'aiohttp.websocket': _aiohttp_logger_config,
                'memority': {
                    'handlers': ['stdout', 'memority_log_file', 'sentry'],
                    'level': 'INFO',
                },
                'monitoring': {
                    'handlers': ['stdout', 'monitoring_log_file', 'sentry'],
                    'level': 'INFO',
                },
                'apscheduler': {
                    'handlers': ['stdout', 'monitoring_log_file', 'sentry'],
                    'level': 'INFO',
                },
            }
        }
    )
    configurator.configure()


log_dir = settings.log_dir
if not os.path.isdir(log_dir):
    os.makedirs(log_dir)

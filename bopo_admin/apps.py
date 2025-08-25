from django.apps import AppConfig
import logging
from logging.handlers import TimedRotatingFileHandler


class BopoAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bopo_admin'
    
    def ready(self):
        logger = logging.getLogger('bopo_backend')
        for handler in logger.handlers:
            if isinstance(handler, TimedRotatingFileHandler):
                handler.suffix = "%Y-%m-%d"

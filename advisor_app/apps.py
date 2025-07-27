
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class AdvisorAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'advisor_app'
    verbose_name = "Advisor Application"

    def ready(self):
        try:
            import advisor_app.signals  # Import signals to connect them
            logger.info("AdvisorApp signals loaded successfully.")
        except ImportError as e:
            logger.error(f"Error importing AdvisorApp signals: {e}")

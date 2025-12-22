from .celery import app as celery_app

__all__ = ("celery_app",)       # for starrting celery as soon as django has started
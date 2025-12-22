import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")   # all celery required variables and data are defined here 

app = Celery("ecommerce")    # app name given for celery by cretaing an instance

app.config_from_object("django.conf:settings", namespace="CELERY")  # celery config to be read starts with namespce defined here

app.autodiscover_tasks()  # configuring celery to auto discover tasks which would be defined in tasks file with @shared_task 

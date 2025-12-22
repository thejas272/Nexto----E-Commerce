from celery import shared_task
from django.utils import timezone
from Nexto.models import OrderItemModel
from accounts.models import AdminAlertModel
from datetime import timedelta


@shared_task
def check_overdue_deliveries():

  today = timezone.now().date()

  overdue_items = OrderItemModel.objects.filter(is_delivered=False,
                                                delivery_date__lt=today)
  
  for overdue_item in overdue_items:
    AdminAlertModel.objects.create(order_item=overdue_item,
                                   user=None,
                                   for_staff=True,
                                   message=f"Delivery overdue for order #{overdue_item.order.order_id} - {overdue_item.name}",
                                  )
    

@shared_task
def reminder_delivery_today():
  today = timezone.now().date()

  items = OrderItemModel.objects.filter(is_delivered=False,
                                        delivery_date=today)
  
  for item in items:
    AdminAlertModel.objects.get_or_create(order_item=item,
                                          user=None,
                                          for_staff=True,
                                          message=f"Delivery scheduled for today for order #{item.order.order_id} - {item.name}",
                                          )
  


@shared_task
def clean_old_admin_alerts():
  cutoff_date = timezone.now() - timedelta(days=7)

  AdminAlertModel.objects.filter(created_at__lt=cutoff_date,
                                 for_staff=True
                                ).delete()


  
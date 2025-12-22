from django import template
from django.utils import timezone

register = template.Library()

# custom template filters for both delivery info display as well as return info display

@register.filter
def delivery_status(item):      # returns delivery info text with date  in order listing template

  day_or_date_cum_prefix = "" 
  today = timezone.now().date()
  yesterday = today - timezone.timedelta(days=1)
  tomorrow  = today + timezone.timedelta(days=1)


  # configuring date info
 
  if item.delivery_date == today:
    day_or_date_cum_prefix = "today"

  elif item.delivery_date == yesterday:
    day_or_date_cum_prefix = "yesterday"
  
  elif item.delivery_date == tomorrow:
    day_or_date_cum_prefix = "tomorrow"
  
  else:
    day_or_date_cum_prefix = f"on {item.delivery_date.strftime("%d %B %Y")}"
  
  # configuring the text to display based on scenario with date info evaluated above

  if item.is_delivered:
    return f"Delivered {day_or_date_cum_prefix}"
  
  if item.is_delivery_overdue:
    return f"Running late, was expected {day_or_date_cum_prefix}"
  
  return f"Arriving {day_or_date_cum_prefix}"




@register.filter
def return_status(item):   # displays return info text in user order listing template  

  if not item.is_delivered:
    return ""
  
  if not item.return_till:
    return "Non returnable item"
  
  if item.is_returnable:
    return f"Return window open until {item.return_till.strftime('%d %B %Y')}"
  
  return f"Return Window closed on {item.return_till.strftime('%d %B %Y')}"
  

  
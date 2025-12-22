from django.db import models
from django.contrib.auth.models import User
import Nexto
# Create your models here.


class StaffLogModel(models.Model):
  staff_user    = models.ForeignKey(User, related_name="staff_logs", on_delete=models.SET_NULL, null=True, blank=True)
  affected_user = models.ForeignKey(User, related_name="affected_logs", on_delete=models.CASCADE, null=True, blank=True)

  field_name  = models.CharField(max_length=300, null=True, blank=True)
  old_value   = models.CharField(max_length=400, null=True, blank=True)
  new_value   = models.CharField(max_length=400, null=True, blank=True)
  description = models.TextField(null=True, blank=True)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name = "Staff log" 
    verbose_name_plural = "Staff logs"

  def __str__(self):
    staff = self.staff_user.username if self.staff_user else "Unknown staff"
    field_name = self.field_name if self.field_name else "Unknown field"
    old_value = self.old_value if self.old_value else "(no previous value)"
    new_value = self.new_value if self.new_value else "(no new value)"
    return f"{staff} updated {field_name} of {self.affected_user.username} from '{old_value}' to '{new_value}'"


class AdminAlertModel(models.Model):
  order_item = models.ForeignKey("Nexto.OrderItemModel", on_delete=models.CASCADE, null=False, blank=False)
  user       = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
  message    = models.TextField(null=False, blank=False)
  seen       = models.BooleanField(default=False)
  for_staff  = models.BooleanField(default=False)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name = "Admin Alert"
    verbose_name_plural = "Admin Alerts"
  
  def __str__(self):
    username = self.user.username if self.user else "Staff"
    item =self.order_item.name if self.order_item else "unknown item"
    return f" For {username} - '{item}' - {self.message}"
   



class AddressModel(models.Model):
  STATE_CHOICES = [ ("AP", "Andhra Pradesh"),
                    ("AR", "Arunachal Pradesh"),
                    ("AS", "Assam"),
                    ("BR", "Bihar"),
                    ("CG", "Chhattisgarh"),
                    ("GA", "Goa"),
                    ("GJ", "Gujarat"),
                    ("HR", "Haryana"),
                    ("HP", "Himachal Pradesh"),
                    ("JH", "Jharkhand"),
                    ("KA", "Karnataka"),
                    ("KL", "Kerala"),
                    ("MP", "Madhya Pradesh"),
                    ("MH", "Maharashtra"),
                    ("MN", "Manipur"),
                    ("ML", "Meghalaya"),
                    ("MZ", "Mizoram"),
                    ("NL", "Nagaland"),
                    ("OD", "Odisha"),
                    ("PB", "Punjab"),
                    ("RJ", "Rajasthan"),
                    ("SK", "Sikkim"),
                    ("TN", "Tamil Nadu"),
                    ("TS", "Telangana"),
                    ("TR", "Tripura"),
                    ("UP", "Uttar Pradesh"),
                    ("UK", "Uttarakhand"),
                    ("WB", "West Bengal"),
                    ("DL", "Delhi"),
                    ("JK", "Jammu & Kashmir"),
                    ("LD", "Lakshadweep"),
                    ("PY", "Puducherry"),
                    ("CH", "Chandigarh"),
                    ]
  
  user = models.ForeignKey(User, related_name='addresses', on_delete=models.CASCADE, null=False, blank=False)
  default_address = models.BooleanField(default=False)

  full_name = models.CharField(max_length=100, null=False, blank=False)
  phone     = models.CharField(max_length=15, null=False, blank=False)
  house     = models.CharField(max_length=100, null=False, blank=False)
  street    = models.CharField(max_length=50, null=False, blank=False)
  city      = models.CharField(max_length=100, null=False, blank=False)
  state     = models.CharField(max_length=10, null=False, blank=False, choices=STATE_CHOICES)
  landmark  = models.CharField(max_length=300, null=False, blank=False)
  pincode   = models.CharField(max_length=6, null=False,blank=False)  


 
  class Meta:
    verbose_name = 'Address'
    verbose_name_plural = 'Addresses'

  def __str__(self):
    return self.full_name
  
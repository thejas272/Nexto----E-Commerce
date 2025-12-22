from django.contrib import admin
from accounts.models import AddressModel,StaffLogModel,AdminAlertModel
# Register your models here.

admin.site.register(AddressModel)
admin.site.register(StaffLogModel)
admin.site.register(AdminAlertModel)
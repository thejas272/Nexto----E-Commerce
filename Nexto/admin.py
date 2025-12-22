from django.contrib import admin
from Nexto.models import CategoryModel, ProductModel, BrandModel, ImageModel, SellerModel, CartModel, OrderModel, OrderItemModel, PaymentModel, ShippingSettings, OrderStatusModel
# Register your models here.
admin.site.register(CategoryModel)
admin.site.register(ProductModel)
admin.site.register(BrandModel)
admin.site.register(ImageModel)
admin.site.register(SellerModel)
admin.site.register(CartModel)
admin.site.register(OrderModel)
admin.site.register(OrderItemModel)
admin.site.register(OrderStatusModel)
admin.site.register(PaymentModel)
admin.site.register(ShippingSettings)
from django.db import models
from django.contrib.auth.models import User
from accounts.models import AddressModel
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
# Create your models here.



class ShippingSettings(models.Model):
  shipping_fee = models.DecimalField(max_digits=10, decimal_places=2)
  handling_fee = models.DecimalField(max_digits=10, decimal_places=2)

  free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2)

  def __str__(self):
    return "Shipping & handling fee"
  

  def clean(self,*args,**kwargs):
    if not self.pk and ShippingSettings.objects.exists():
      raise ValidationError("Only one shipping settings must exist")
    super().save(*args,**kwargs)

  class Meta:
    verbose_name = "Shipping Setting"
    verbose_name_plural = "Shipping Settings"



class BrandModel(models.Model):
  created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='brand_created', null=True, blank=True)
  updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='brand_updated', null=True, blank=True)

  name = models.CharField(max_length=100, null=False, blank=False)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name_plural = 'Brands'
    verbose_name = 'Brand'

  def __str__(self):
    return self.name


class CategoryModel(models.Model):
  UNIT_CHOICES = [('hours','Hours'),
                  ('days','Days')]

  created_by = models.ForeignKey(User, related_name='category_created', on_delete=models.SET_NULL, null=True, blank=True)
  updated_by = models.ForeignKey(User, related_name='category_updated', on_delete=models.SET_NULL, null=True, blank=True)

  name       = models.CharField(max_length=100, unique=True, null=False, blank=False) 

  return_window_value   = models.PositiveIntegerField(null=False, blank=False)   # value 0 considered as non returnable
  return_window_unit    = models.CharField(max_length=10, null=True, blank=True, choices=UNIT_CHOICES, default="days")
  delivery_window_value = models.PositiveIntegerField(null=False, blank=False)
  delivery_window_unit  = models.CharField(max_length=10, null=False, blank=False, choices=UNIT_CHOICES, default="days")

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.name
  
  def save(self,*args,**kwargs):
    if self.return_window_value == 0:
      self.return_window_unit = None
    
    elif not self.return_window_unit:
      self.return_window_unit = "days"
    super().save(*args,**kwargs)
  

  class Meta:
    verbose_name = "Category"
    verbose_name_plural = "Categories"

  
class SellerModel(models.Model):
  created_by = models.ForeignKey(User, related_name='seller_created', on_delete=models.SET_NULL, null=True, blank=True)
  updated_by = models.ForeignKey(User, related_name='seller_updated', on_delete=models.SET_NULL, null=True, blank=True)

  name       = models.CharField(max_length=100, null=False, blank=False)
  address    = models.CharField(max_length=250, null=False, blank=False)
  email      = models.EmailField(max_length=50, null=False, blank=False)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name_plural = 'Sellers'
    verbose_name = 'Seller'

  def __str__(self):
    return self.name
  


class ProductModel(models.Model):
  UNIT_CHOICES=[('kg','kilogram'),
                ('g','Gram'),
                ('piece','Piece'),
                ('ml','Millilitre'),
                ('l','Litre'),
                ('pack','Pack'),]
  
  category    = models.ForeignKey(CategoryModel, related_name='products', on_delete=models.CASCADE, null=False, blank=False) 
  brand       = models.ForeignKey(BrandModel, related_name='products', on_delete=models.CASCADE, null=True, blank=True)
  seller      = models.ForeignKey(SellerModel, related_name='products', on_delete=models.CASCADE, null=True, blank=True)
  created_by  = models.ForeignKey(User, related_name='product_created', on_delete=models.SET_NULL, null=True, blank=True)
  updated_by  = models.ForeignKey(User, related_name='product_updated', on_delete=models.SET_NULL, null=True, blank=True)

  name        = models.CharField(max_length=500, unique=True, null=False, blank=False)
  unit        = models.CharField(max_length=10, choices=UNIT_CHOICES, null=False, blank=False)
  quantity    = models.IntegerField(null=False, blank=False)
  weight_per_unit = models.FloatField(null=True, blank=True)
  description = models.TextField(null=False, blank=False)
  price       = models.DecimalField(null=False, blank=False, max_digits=12, decimal_places=2)
  image       = models.ImageField(upload_to='product_images/', null=False, blank=False)

 

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name = "Product"
    verbose_name_plural = "Products"

  def __str__(self):
    return self.name




class ImageModel(models.Model):
  created_by = models.ForeignKey(User, related_name='image_created', on_delete=models.SET_NULL, null=True, blank=True)
  updated_by = models.ForeignKey(User, related_name='image_updated', on_delete=models.SET_NULL, null=True, blank=True)
  product    = models.ForeignKey(ProductModel, related_name='images', on_delete=models.CASCADE, null=False, blank=False)


  image      = models.ImageField(upload_to='product_images/',null=False, blank=False)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name_plural = 'Images'
    verbose_name = 'Image'

  def __str__(self):
    return f"image of {self.product.name}"






class CartModel(models.Model):
  user     = models.ForeignKey(User, related_name='products_in_cart', on_delete=models.CASCADE, null=False, blank=False)
  product  = models.ForeignKey(ProductModel, related_name='products', on_delete=models.CASCADE, null=False, blank=False)
  quantity = models.PositiveIntegerField(null=False, blank=False, default=1)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  @property
  def total_price(self):
    return self.product.price * self.quantity
  

  @property
  def total_weight(self):
    result = self.product.quantity * self.quantity
    return f"{result} {self.product.unit}"
  
  @property
  def num_of_products(self):
    return 



  class Meta:
    unique_together = ('user','product')
    verbose_name = 'Cart'
    verbose_name_plural = 'Carts'
     
  def __str__(self):
    return f"{self.user.username} -  {self.product.name}"
  




class PaymentModel(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
  
  razorpay_order_id     = models.CharField(max_length=200, unique=True, null=True, blank=True)
  razorpay_payment_id   = models.CharField(max_length=200, null=True ,blank=True)
  razorpay_signature    = models.CharField(max_length=300, null=True, blank=True)

  amount = models.FloatField()
  status = models.CharField(max_length=30, default="CREATED")
  # CREATED / SUCCESS / FAILED / COD

  address      = models.ForeignKey(AddressModel, on_delete=models.SET_NULL, null=True, blank=True)
  subtotal     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  handling_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  payment_method = models.CharField(max_length=100, null=True, blank=True)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


  def __str__(self):
    return f"{self.user.username} - {self.razorpay_payment_id} - {self.amount}"

  class Meta:
    verbose_name = "Payment"
    verbose_name_plural = "Payments"

  

class OrderModel(models.Model):
  address      = models.ForeignKey(AddressModel, related_name='orders', on_delete=models.SET_NULL, null=True, blank=True)
  user         = models.ForeignKey(User, related_name='orders',on_delete=models.SET_NULL, null=True, blank=True)
  payment      = models.OneToOneField(PaymentModel, related_name='order', on_delete=models.SET_NULL, null=True, blank=True)

  subtotal     = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
  shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0)
  handling_fee = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0)
  total        = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)

  payment_method = models.CharField(max_length=100, null=False, blank=False)
  
  
  order_id       = models.CharField(max_length=100,unique=True, editable=False)
  delivery_date  = models.DateField(null=True, blank=True)
  return_till    = models.DateField(null=True, blank=True) 

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


  class Meta:
    verbose_name = "Order"
    verbose_name_plural = "Orders"

  def save(self, *args, **kwargs):
    if not self.order_id:
      self.order_id = "ORD"+uuid.uuid4().hex[:10].upper()

    if not self.delivery_date:
      self.delivery_date = timezone.now().date() + timedelta(days=1)
      
    if not self.return_till:
      self.return_till = timezone.now().date() + timedelta(days=14)
    super().save(*args, **kwargs)

  @property
  def all_delivered(self):
    if not self.items.exists():
      return False
    
    items = self.items.all()
    
    for item in items:
      if not item.is_delivered:
        return False
    return True

  def __str__(self):
    return self.order_id
  

class OrderItemModel(models.Model):
  STATUS_CHOICES = [
                  ("placed", "Order Placed"),
                  ("confirmed", "Order Confirmed"),
                  ("packed", "Packed"),
                  ("shipped", "Shipped"),
                  ("out_for_delivery", "Out for Delivery"),
                  ("delivered", "Delivered"),
                  ("cancelled", "Cancelled"),
                  ("returned", "Returned"),
                  ]
  
  order   = models.ForeignKey(OrderModel, related_name='items', on_delete=models.CASCADE, null=False, blank=False)
  product = models.ForeignKey(ProductModel, related_name='on_orders', on_delete=models.SET_NULL, null=True, blank=True)
  
  is_delivered = models.BooleanField(default=False, null=False, blank=False)

  name              = models.CharField(max_length=100, null=False, blank=False)
  brand             = models.CharField(max_length=100, null=True, blank=True)
  category          = models.CharField(max_length=100, null=False, blank=False)
  image             = models.ImageField(upload_to='order_images/', null=False, blank=False)
  order_status      = models.CharField(max_length=40, null=False, blank=False, choices=STATUS_CHOICES, default='placed')
  
  unit              = models.CharField(max_length=50, null=False, blank=False)
  unit_quantity     = models.IntegerField(null=False, blank=False)
  weight_per_unit   = models.FloatField(null=True, blank=True)
  price             = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
  quantity          = models.PositiveIntegerField(null=False, blank=False)
  total             = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)

  return_till   = models.DateTimeField(null=True, blank=True)
  delivery_date = models.DateField(null=False, blank=False) 
  created_at    = models.DateTimeField(auto_now_add=True)
  updated_at    = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name = "OrderItem"
    verbose_name_plural ="OrderItems"


  @property
  def is_returnable(self):
    if not self.return_till:
      return False
    
    today = timezone.now()
    return today <= self.return_till
  
  @property      
  def is_delivery_overdue(self): # to check and display the message in template to user using templatetags filter
    if not self.delivery_date or self.is_delivered:
      return False
    
    today = timezone.now().date()    
    return self.delivery_date < today


  def __str__(self):
    return f"{self.order.order_id} - {self.name} - {self.created_at.date()}"
  


class OrderStatusModel(models.Model):
  STATUS_CHOICES = [
                  ("placed", "Order Placed"),
                  ("confirmed", "Order Confirmed"),
                  ("packed", "Packed"),
                  ("shipped", "Shipped"),
                  ("out_for_delivery", "Out for Delivery"),
                  ("delivered", "Delivered"),
                  ("cancelled", "Cancelled"),
                  ("returned", "Returned"),
                  ]
  
  order_item = models.ForeignKey(OrderItemModel, on_delete=models.CASCADE, related_name="status_updates", null=False, blank=False)
  updated_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="status_updates") 

  status      = models.CharField(max_length=50, null=False, blank=False, choices=STATUS_CHOICES)
  description = models.TextField(null=True, blank=True) 

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name = "Order Status Update"
    verbose_name_plural = "Order Status Updates"

  def __str__(self):
    return f"{self.order_item.order.order_id} - {self.order_item.name} - {self.get_status_display()}"
  




class ContactModel(models.Model):
  name    = models.CharField(max_length=200, null=False, blank=False)
  email   = models.EmailField(max_length=200, null=False, blank=False)
  message = models.TextField(null=False, blank=False)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


  class Meta:
    verbose_name = "Contact"
    verbose_name_plural = "Contacts"

  def __str__(self):
    return self.name
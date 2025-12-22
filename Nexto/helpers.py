from Nexto.models import CartModel
from Nexto.models import ShippingSettings





def get_cart_count(user):
  if not user.is_authenticated:
    return 0
  
  return sum(cart_item.quantity for cart_item in CartModel.objects.filter(user=user))



def fee_calculate(subtotal):
  fee = ShippingSettings.objects.first()
  shipping_fee = fee.shipping_fee
  handling_fee = fee.handling_fee
  free_shipping_threshold= fee.free_shipping_threshold
  total = 0

  if subtotal <= free_shipping_threshold:
    total = subtotal + shipping_fee + handling_fee
  else:
    shipping_fee = 0
    total = subtotal + handling_fee

  return subtotal,shipping_fee,handling_fee,total

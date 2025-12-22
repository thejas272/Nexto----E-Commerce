from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from Nexto.models import CategoryModel,ProductModel,BrandModel,ImageModel,CartModel,ContactModel,PaymentModel,OrderModel,OrderItemModel,ShippingSettings,OrderStatusModel
from Nexto.forms import ContactForm
from accounts.models import AddressModel
from django.core.paginator import Paginator
from django.db.models import Q
from Nexto.helpers import get_cart_count,fee_calculate
import razorpay
import json
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone



def index(request):
  categories = CategoryModel.objects.all()
  all_products = ProductModel.objects.order_by('-created_at')

  fruits = all_products.filter(category__name="Fruit").all()
  vegetables = all_products.filter(category__name="Vegetable").all()
  breads = all_products.filter(category__name="Bread").all()
  meats  = all_products.filter(category__name="Meat").all()

  category_products = {}

  for category in categories:
    products = ProductModel.objects.filter(category=category).order_by('-created_at')[:2]

    category_products[category] = products
  
  contain_products = ProductModel.objects.exists()
     
  cart_count = get_cart_count(request.user)
  return render(request,'index.html',{'category_products':category_products,'contain_products':contain_products,'fruits':fruits,'vegetables':vegetables,'breads':breads,'meats':meats,'cart_count':cart_count})



def cart(request):
  if request.user.is_authenticated:
    cart_items = CartModel.objects.filter(user=request.user)
    cart_count = get_cart_count(request.user)


    sub_total = sum(item.total_price for item in cart_items)

    sub_total,shipping_fee,handling_fee,cart_total= fee_calculate(sub_total)

   
    return render(request,'cart.html',{'cart_items':cart_items,'cart_count':cart_count,'sub_total':sub_total,'cart_total':cart_total,'shipping_fee':shipping_fee,'handling_fee':handling_fee})
  
  return render(request,'cart.html')





def update_cart(request):
  if not request.user.is_authenticated:
    return redirect('login')
  
  product_id = request.POST.get('product_id')
  action     = request.POST.get('action')
  quantity   = request.POST.get('quantity')

  if not product_id or not action:
    return redirect('cart')
  
  cart_item = CartModel.objects.filter(product_id=product_id,user=request.user).first()

  if cart_item and action == "increase":
    cart_item.quantity +=1
    cart_item.save()

  elif cart_item and action == "decrease":
    
    if cart_item.quantity <= 1:
      cart_item.delete()
    else:
      cart_item.quantity -= 1
      cart_item.save()
     

  elif cart_item and action == "remove":
    cart_item.delete()
  
  elif action == "add":

    if cart_item:
      cart_item.quantity += 1
      cart_item.save()
    else:
      product=ProductModel.objects.get(id=product_id)
      CartModel.objects.create(user=request.user,
                               product=product,
                               quantity=quantity if quantity else 1,
                             )
    return redirect('shop')

  return redirect('cart')






def contact(request):
  cart_count = get_cart_count(request.user)
  return render(request,'contact.html',{'cart_count':cart_count})


def testimonial(request):
  cart_count = get_cart_count(request.user)
  return render(request,'testimonial.html',{'cart_count':cart_count})


def checkout(request):
  if not request.user.is_authenticated:
    return redirect('cart')
  
  cart_items = CartModel.objects.filter(user=request.user)
  if not cart_items:
    return redirect('shop')

  delivery_address=AddressModel.objects.filter(default_address=True,user=request.user).first()
  
  # to handle change of address case, request coming from checkout_address.html page
  if request.method == "POST":
    address_id = request.POST.get('address_id',None)
    if address_id:
      delivery_address = AddressModel.objects.get(id=address_id)
  

  
  cart_count = get_cart_count(request.user)

  state_choices = AddressModel.STATE_CHOICES


  sub_total = sum(item.total_price for item in cart_items)

  sub_total,shipping_fee,handling_fee,cart_total = fee_calculate(sub_total)

  return render(request,'checkout.html',{'delivery_address':delivery_address,'cart_items':cart_items,'handling_fee':handling_fee,'shipping_fee':shipping_fee,'cart_count':cart_count,'sub_total':sub_total,'cart_total':cart_total,'state_choices':state_choices})




def start_payment(request):
  if not request.user.is_authenticated:
    return redirect('login')
  
  if request.method == "POST":
    cart_items = CartModel.objects.filter(user=request.user)

    address_id = request.POST.get('address_id',None)
    payment_method = request.POST.get('payment_method',None)

    if not payment_method:
      messages.error(request,'Payment method not found.', extra_tags='payment_method_message')
      return redirect('checkout')
    
    try:
      delivery_address = AddressModel.objects.get(id=address_id,user=request.user)
    except AddressModel.DoesNotExist:
      messages.error(request,'Invalid address selected',extra_tags='address_message')
      return redirect('checkout')
    

    sub_total = sum(cart_item.total_price for cart_item in cart_items)

    sub_total,shipping_fee,handling_fee,total_amount = fee_calculate(sub_total)


    if payment_method == "cod":
      payment = PaymentModel.objects.create(user=request.user,
                                  amount=total_amount,
                                  status="SUCCESS",
                                  address=delivery_address,
                                  subtotal=sub_total,
                                  shipping_fee=shipping_fee,
                                  handling_fee=handling_fee,
                                  payment_method="cod"
                                  )
      return redirect('cod_payment',payment_id=payment.id)



    razorpay_amount_paise = int(total_amount*100)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    razorpay_order= client.order.create({"amount":razorpay_amount_paise,
                                         "currency":"INR",
                                         "payment_capture":"1"})
    
    payment = PaymentModel.objects.create(
                                user=request.user,
                                razorpay_order_id = razorpay_order['id'],
                                amount = total_amount,
                                status = "CREATED",
                                address=delivery_address,
                                subtotal=sub_total,
                                shipping_fee=shipping_fee,
                                handling_fee=handling_fee,
                                payment_method=payment_method
                                )
    
    return render(request,'razorpay_checkout.html',{
                                                  'order':razorpay_order,
                                                  'key_id':settings.RAZORPAY_KEY_ID,
                                                  'payment':payment,
                                                  'cart_items':cart_items,
                                                  'amount':total_amount
                                                  })


def verify_payment(request):
  if not request.user.is_authenticated:
    return redirect('login')
  
  if request.method == "POST":
    

    razorpay_order_id   = request.POST.get('razorpay_order_id',None).strip()
    razorpay_payment_id = request.POST.get('razorpay_payment_id',None).strip()
    razorpay_signature  = request.POST.get('razorpay_signature',None).strip()

    cart_items = CartModel.objects.filter(user=request.user)
    payment = PaymentModel.objects.filter(razorpay_order_id=razorpay_order_id).first()

    if not payment:
      return redirect('payment_failed',payment_id=0)
    

    if not razorpay_order_id:
      payment.status = "FAILED"
      payment.save()
      cart_items.delete()
      return redirect('payment_failed',payment_id=0)
    
    

    if not razorpay_payment_id or not razorpay_signature:
      payment.status = "FAILED"
      payment.save()
      cart_items.delete()
      return redirect('payment_failed',payment_id=payment.id)



    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


    try:
      # when payment is sucessfull
      client.utility.verify_payment_signature({'razorpay_order_id':razorpay_order_id,
                                               'razorpay_payment_id':razorpay_payment_id,
                                               'razorpay_signature':razorpay_signature
                                              })
    

      payment_details = client.payment.fetch(razorpay_payment_id)
      if payment_details.get('status') != "captured":
        payment.status = "FAILED"
        payment.payment_method = payment_details.get('method')
        payment.save()
        cart_items.delete()
        return redirect('payment_failed',payment_id=payment.id)



      # in case of duplication of payment  
      if payment.status == "SUCCESS" and hasattr(payment,"order"):
        return redirect('payment_success',payment_id=payment.id)
      



      razorpay_order = client.order.fetch(razorpay_order_id)
      # in case of incorrect amount 
      if payment.amount*100 != razorpay_order['amount']:
        payment.status = "FAILED"
        payment.payment_method = payment_details.get('method')
        payment.save()
        cart_items.delete()
        return redirect('payment_failed',payment_id=payment.id)

      
      # updating the payment model created at the start of payment
      payment.razorpay_payment_id = razorpay_payment_id
      payment.razorpay_signature = razorpay_signature
      payment.payment_method = payment_details.get('method')  # from razorpay client payment info
      payment.status = "SUCCESS"
      payment.save()

      # creating order record for this order
      order = OrderModel.objects.create(user=request.user,
                                        payment=payment,
                                        address=payment.address,
                                        subtotal=payment.subtotal,
                                        shipping_fee=payment.shipping_fee,
                                        handling_fee=payment.handling_fee,
                                        total=payment.amount,
                                        payment_method=payment.payment_method
                                        )
      

      # creating order item records for all items in this order
      order_item_records_to_be_created=[]
      today = timezone.now()

      for cart_item in cart_items:

        category = cart_item.product.category
        return_till_date = None
        delivery_date = None

        if category.delivery_window_unit == "days":
          delivery_date = today + timedelta(days=category.delivery_window_value)
        elif category.delivery_window_unit == "hours":
          delivery_date = today + timedelta(hours=category.delivery_window_value)
        


        if category.return_window_value == 0:
          return_till_date = None
        else:
          if category.return_window_unit == "hours":
            return_till_date = today + timedelta(hours=category.return_window_value)
          elif category.return_window_unit == "days":
            return_till_date = today + timedelta(days=category.return_window_value)
      

        order_item_records_to_be_created.append(OrderItemModel(order=order,
                                                              product=cart_item.product,
                                                              name=cart_item.product.name,
                                                              brand=cart_item.product.brand.name if cart_item.product.brand else "",
                                                              category=cart_item.product.category.name if cart_item.product.category else "",
                                                              image=cart_item.product.image,
                                                              order_status="placed",
                                                              unit=cart_item.product.unit,
                                                              unit_quantity=cart_item.product.quantity,
                                                              weight_per_unit=cart_item.product.weight_per_unit,
                                                              price=cart_item.product.price,
                                                              quantity=cart_item.quantity,
                                                              total=cart_item.total_price,
                                                              delivery_date=delivery_date,
                                                              return_till=return_till_date
                                                              )
                                                )
        

      OrderItemModel.objects.bulk_create(order_item_records_to_be_created)

      order_items = OrderItemModel.objects.filter(order=order)
      order_status_records_to_be_created = []
      for item in order_items:
        order_status_records_to_be_created.append(OrderStatusModel(order_item=item,
                                                  status=item.order_status
                                                  ))
      
      OrderStatusModel.objects.bulk_create(order_status_records_to_be_created)
      cart_items.delete()


      return redirect('payment_success',payment_id=payment.id)
      
    except:
      # when payment failed updating the payment record to depict that 
      payment.status = "FAILED"
      payment.razorpay_payment_id = razorpay_payment_id
      payment.save()
      return redirect('payment_failed',payment_id=payment.id)
      
    

def cod_payment(request,payment_id):
  if not request.user.is_authenticated:
    return redirect('login')
  
  payment_id = payment_id

  try:
    payment = PaymentModel.objects.get(user=request.user,id=payment_id)
  except PaymentModel.DoesNotExist:
    messages.error(request,'Invalid payment method', extra_tags="payment_method_message")
    return redirect('checkout') 
  

  if hasattr(payment,'order'):
    return redirect('payment_success',payment_id=payment.id)

  
  cart_items = CartModel.objects.filter(user=request.user)
  
  order=OrderModel.objects.create(user=request.user,
                            address=payment.address,
                            payment=payment,
                            subtotal=payment.subtotal,
                            shipping_fee=payment.shipping_fee,
                            handling_fee=payment.handling_fee,
                            total=payment.amount,
                            payment_method=payment.payment_method
                            )
  
  order_item_records_to_be_created=[]
  today = timezone.now()

  for cart_item in cart_items:
    return_till_date = None
    category = cart_item.product.category

    if category.return_window_value == 0:
      return_till_date = None
    else:
      if category.return_window_unit == "days":
        return_till_date = today + timedelta(days=category.return_window_value)
      elif category.return_window_unit == "hours":
        return_till_date = today + timedelta(hours=category.return_window_value)

    order_item_records_to_be_created.append(OrderItemModel(order=order,
                                                           product=cart_item.product,
                                                           name=cart_item.product.name,
                                                           brand=cart_item.product.brand.name if cart_item.product.brand else "",
                                                           category=cart_item.product.category.name if cart_item.product.category else "",
                                                           image=cart_item.product.image,
                                                           order_status="placed",
                                                           unit=cart_item.product.unit,
                                                           unit_quantity=cart_item.product.quantity,
                                                           weight_per_unit=cart_item.product.weight_per_unit,
                                                           price=cart_item.product.price,
                                                           quantity=cart_item.quantity,
                                                           total=cart_item.total_price,
                                                           delivery_date=today + timedelta(days=1),
                                                           return_till=return_till_date,
                                                           )
                                            )
  OrderItemModel.objects.bulk_create(order_item_records_to_be_created)

  order_items = OrderItemModel.objects.filter(order=order)
  order_status_records_to_be_created = []
  for item in order_items:
    order_status_records_to_be_created.append(OrderStatusModel(order_item=item,
                                                               status=item.order_status
                                                               ))
  

  OrderStatusModel.objects.bulk_create(order_status_records_to_be_created)
  cart_items.delete()
  return redirect('payment_success',payment_id=payment.id)


  


def payment_success(request,payment_id):
  if not request.user.is_authenticated:
    return redirect('login')
  
  payment = None
  order = None

  if payment_id:
    payment = PaymentModel.objects.filter(id=payment_id,user=request.user).first()

  if payment and hasattr(payment,'order'):
    order=payment.order

  return render(request,'payment_success.html',{"payment_id":payment.razorpay_payment_id if payment and payment.razorpay_payment_id else None,
                                                "amount":payment.amount if payment and payment.amount else None,
                                                "order_id":order.order_id if order else None
                                               })


  


def payment_failed(request,payment_id):
  if not request.user.is_authenticated:
    return redirect('login')
  

  payment = None
  order = None
  
  if payment_id and payment_id != 0:
    payment = PaymentModel.objects.filter(id=payment_id,user=request.user).first()
  
  if payment and hasattr(payment,'order'):
    order=payment.order

  return render(request,'payment_failed.html',{"payment_id":payment.razorpay_payment_id if payment and payment.razorpay_payment_id else None,
                                               "order_id":order.order_id if order else None,
                                               "amount":payment.amount if payment and payment.amount else None
                                              })





def delivery_address_select(request):
  if not request.user.is_authenticated:
    return redirect('login')
  
  state_choices = AddressModel.STATE_CHOICES
  addresses  = AddressModel.objects.filter(user=request.user)
  cart_items = CartModel.objects.filter(user=request.user)
  cart_count = get_cart_count(request.user)

  shipping_fee,handling_fee = 45,10
  sub_total = sum(cart_item.total_price for cart_item in cart_items)
  if sub_total <= 299:
    cart_total = sub_total + shipping_fee + handling_fee
  else:
    cart_total = sub_total + handling_fee

  return render(request,'checkout_addresses.html',{'addresses':addresses,'state_choices':state_choices,'cart_count':cart_count,'cart_items':cart_items,'sub_total':sub_total,'cart_total':cart_total,'shipping_fee':shipping_fee,'handling_fee':handling_fee})





def shop(request):
  all_products = ProductModel.objects.all()
  categories = CategoryModel.objects.order_by('name')
  brands = BrandModel.objects.all().order_by('name')

  category_id = request.GET.get('category')
  price = request.GET.get('price')
  brand = request.GET.get('brand')
  sort = request.GET.get('filter')


  search = request.GET.get('search')
  if search:
    all_products = all_products.filter(Q(name__icontains=search) | Q(description__icontains=search) | Q(category__name__icontains=search) |Q(brand__name__icontains=search))


  if sort == "price_a":
    all_products =  all_products.order_by('price')
  elif sort == "price_d":
    all_products = all_products.order_by('-price')
  elif sort == "date_d":
    all_products = all_products.order_by('-created_at')


  if category_id:
    all_products = all_products.filter(category_id=category_id)

  if price:
    all_products = all_products.filter(price__lte=price)
  
  if brand:
    all_products = all_products.filter(brand_id=brand)

  paginator = Paginator(all_products,12)
  page_number = request.GET.get('page')
  page_object = paginator.get_page(page_number)

  cart_count = get_cart_count(request.user)
  return render(request,'shop.html',{'categories':categories,'brands':brands,'page_object':page_object,'cart_count':cart_count})



def shop_detail(request,product_id):
  products = ProductModel.objects.all()

  images  = ImageModel.objects.filter(product_id=product_id).all()
  product = products.filter(id=product_id).first()
  related_products = products.filter(category=product.category).exclude(id=product.id)
  cart_count = get_cart_count(request.user)
  shipping = ShippingSettings.objects.first()

  return render(request,'shop-detail.html',{'product':product,'images':images,'related_products':related_products,'cart_count':cart_count,'shipping':shipping})





def contact_submission(request):

  if request.method == "POST":
    form = ContactForm(request.POST)

    if form.is_valid():
      ContactModel.objects.create(
        name    = form.cleaned_data['name'],
        email   = form.cleaned_data['email'],
        message = form.cleaned_data['message']
      )
      messages.info(request,"Thanks for reaching out to us, our team is working on it and woruld get back to you with a follow up.",extra_tags='contact_form_message')
      return redirect('contact')
    
    cart_count = get_cart_count(request.user)
    return render(request,'contact.html',{'form':form,'cart_count':cart_count})
  




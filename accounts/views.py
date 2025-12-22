from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages
from accounts.forms import UserLoginForm,UserRegisterForm,AddAddressForm
from accounts.models import AddressModel,StaffLogModel,AdminAlertModel
from Nexto.models import CartModel,OrderModel, OrderItemModel, OrderStatusModel
from Nexto.helpers import get_cart_count
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
# Create your views here.

def login(request):
  if request.user.is_authenticated:
    return redirect('index')
  
  if request.method == "POST":
    form = UserLoginForm(request.POST)

    if form.is_valid():
      user = auth.authenticate(username=form.cleaned_data['username'],password=form.cleaned_data['password'])

      if not user:
        messages.error(request,"Invalid username or password",extra_tags='login_message')
        return render(request,'login.html',{'form':form})

      auth.login(request,user)

      if user.is_staff:
        return redirect('admin_profile')

      return redirect('index')
      
    return render(request,'login.html',{'form':form})
      

  return render(request,'login.html')


def logout(request):
  if not request.user.is_authenticated:
    return redirect('index')
  
  auth.logout(request)
  return redirect('login')



def register(request):
  if request.method == "POST":
    form = UserRegisterForm(request.POST)
    if form.is_valid():
      User.objects.create_user(first_name = form.cleaned_data['first_name'],
                          last_name  = form.cleaned_data['last_name'],
                          email      = form.cleaned_data['email'],
                          username   = form.cleaned_data['username'],
                          password   = form.cleaned_data['password']
                          )
      return redirect('login')
      
    return render(request,'register.html',{'form':form})  

  return render(request,'register.html')


# Admin Views
def admin_profile(request):
  if not request.user.is_authenticated or not request.user.is_staff:
    return redirect('login')
  
  alert_count = AdminAlertModel.objects.filter(seen=False,for_staff=True).count()

  return render(request,'admin_profile.html',{'alert_count':alert_count})



# Ajax View
def search_users(request):
  if not request.user.is_authenticated or not request.user.is_staff:
    return redirect('login')
  
  q=request.GET.get('q',"")
  users = User.objects.filter(Q(username__icontains=q) | Q(email__icontains=q))
  data = {
        "results": [
            {"username": u.username, "email": u.email, "id": u.id}
            for u in users
        ]
    }
  return JsonResponse(data)


def admin_order_list(request):
  if not request.user.is_authenticated or not request.user.is_staff:
    return redirect('login')
  start_date = request.GET.get('start_date',None)
  end_date   = request.GET.get('end_date',None)
  status     = request.GET.get('status',None)
  uid        = request.GET.get('uid',None)    # from ajax script 
  query = Q()
 
  if start_date:
    query &= Q(created_at__date__gte=start_date)
  if end_date:
    query &= Q(created_at__date__lte=end_date)
  if status:
    query &= Q(items__order_status = status) 
  if uid and uid.isdigit():
    query &= Q(user__id=int(uid))



  orders = OrderModel.objects.filter(query).distinct().order_by('-created_at').all()
   
  paginator = Paginator(orders,10)
  page_number = request.GET.get('page',1)

  page_object = paginator.get_page(page_number)
  status_choices = OrderStatusModel.STATUS_CHOICES

  alert_count = AdminAlertModel.objects.filter(seen=False,for_staff=True).count()


  return render(request,'admin_order_list.html',{'page_object':page_object,'status_choices':status_choices,'alert_count':alert_count})

  
def admin_customer_list(request):
  if not request.user.is_authenticated or not request.user.is_staff:
    return redirect('login')
  
  customers = User.objects.filter(is_staff=False).order_by('-date_joined')

  paginator = Paginator(customers,10)

  page_number = request.GET.get('page',1)
  page_object = paginator.get_page(page_number)
  alert_count = AdminAlertModel.objects.filter(seen=False, for_staff=True).count()

  return render(request,'admin_customer_list.html',{'page_object':page_object,'alert_count':alert_count})

def staff_log(request):
  if not request.user.is_authenticated or not request.user.is_staff:
    return redirect('login')
  
  uid        = request.GET.get('uid',None)
  start_date = request.GET.get('start_date',None)
  end_date   = request.GET.get('end_date',None)
  query = Q()
  if uid and uid.isdigit():
    query &= Q(affected_user_id=uid)
  if start_date:
    query &= Q(created_at__gte=start_date)
  if end_date:
    query &= Q(created_at__lte=end_date)


  logs = StaffLogModel.objects.filter(query)
  paginator = Paginator(logs,10)

  page_number = request.GET.get('page',1)

  page_object = paginator.get_page(page_number)
  alert_count = AdminAlertModel.objects.filter(seen=False,for_staff=True).count()

  return render(request,'admin_log_list.html',{'page_object':page_object,'alert_count':alert_count})
  


def admin_alert_list(request):
  if not request.user.is_authenticated or not request.user.is_staff:
    return redirect('login')
  
  query = Q()
  start = request.GET.get('start_date')
  end   = request.GET.get('end_date')
  
  admin_alerts = AdminAlertModel.objects.filter(for_staff=True).order_by('-created_at')

  if start:
    query &= Q(created_at__date__gte=start)
  if end:
    query &= Q(created_at__date__lte=end) 

  seen_alerts_qs = admin_alerts.filter(query,seen=True)
  unseen_alerts_qs = admin_alerts.filter(seen=False)


  unseen_alerts = list(unseen_alerts_qs)
  seen_alerts = list(seen_alerts_qs)
  
  alert_count = unseen_alerts_qs.count()

  if unseen_alerts_qs.exists():
    unseen_alerts_qs.update(seen=True)

  paginator = Paginator(seen_alerts,15)
  page_number = request.GET.get('page',1)

  page_object = paginator.get_page(page_number) # page object consists of seen alerts
  

  return render(request,'admin_alert_list.html',{'unseen_alerts':unseen_alerts,'page_object':page_object,'alert_count':alert_count})





def admin_order_info(request,order_id):
  if not request.user.is_authenticated or not request.user.is_staff:
    return redirect('login')


  order = OrderModel.objects.filter(id=order_id).first()
  if not order:
    messages.error(request,"Invalid order info",extra_tags="order_na")
    return redirect('admin_order_list')
  
  
  status_choices = OrderStatusModel.STATUS_CHOICES
  alert_count = AdminAlertModel.objects.filter(seen=False,for_staff=True).count()
  
  return render(request,'admin_order_info.html',{'order':order,'status_choices':status_choices,'alert_count':alert_count})

  
def admin_order_status_update(request):
  if not request.user.is_authenticated or not request.user.is_staff:
    return redirect('login')
  
  order_item_id = request.POST.get('order_item_id',None)
  order_id = request.POST.get('order_id',None)
  status = request.POST.get('status',None)

  order_item = OrderItemModel.objects.filter(id=order_item_id).first()
  if not order_item:
    messages.error(request,'Invalid order info')
    return redirect('admin_order_info',order_id=order_id)
  elif not status:
    messages.error(request,'Invalid status info')
    return redirect('admin_order_info',order_id=order_id)
  
  old_value = order_item.order_status
  new_value = status
  affected_user = order_item.order.user
  description = f"Order status of '{affected_user.username}' changed from '{old_value}' to '{new_value}'"

  OrderStatusModel.objects.create(order_item=order_item,
                                  updated_by=request.user,
                                  status=status,
                                  )
  
  order_item.order_status=status
  if status == "delivered":
    category = order_item.product.category

    order_item.delivery_date = timezone.now().date()
    order_item.is_delivered = True 
    
    if category.return_window_value != 0:
      if category.return_window_unit == "hours":
        order_item.return_till = timezone.now() + timedelta(hours=category.return_window_value)
      elif category.return_window_unit == "days":
        order_item.return_till = timezone.now() + timedelta(days=category.return_window_value)

  order_item.save()

  StaffLogModel.objects.create(staff_user = request.user,
                               affected_user = affected_user,
                               field_name = 'order_status',
                               old_value=old_value,
                               new_value=new_value,
                               description=description
                               )

  request.session['last_updated'] = order_item.order.id

  return redirect('admin_order_info',order_id=order_id)
  


  

# User Views
def user_profile(request):
  if not request.user.is_authenticated:
    return redirect('index')
  
  cart_count = get_cart_count(request.user)
  return render(request,'user_profile.html',{'cart_count':cart_count})


def order_list(request):
  if not request.user.is_authenticated:
    return redirect('login')
  
  cart_count = get_cart_count(request.user)
  # retrieves the related order record from OrderModel when query first executes and prevents lazy loading which otherwise happens at template rendering 
  orders = OrderModel.objects.filter(user=request.user).order_by('-created_at')

  
  paginator = Paginator(orders,10)
  page_number = request.GET.get('page',1)
  
  page_object = paginator.get_page(page_number)
  
  return render(request,'order_list.html',{'cart_count':cart_count,'orders':orders,'page_object':page_object})


def order_track(request):
  if not request.user.is_authenticated:
    return redirect('login')
  
  order_item_id = request.POST.get('order_item_id',None)
  order_status = OrderStatusModel.objects.filter(order_item_id=order_item_id)

  if not order_status:
    messages.error(request,"Incorrect order info")
    return redirect('order_list')

  return render(request,'order_track.html',{'order_status':order_status})


def address_list(request):
  if not request.user.is_authenticated:
    return redirect('login')
  
  cart_count = get_cart_count(request.user)
  addresses = AddressModel.objects.filter(user=request.user).order_by('-default_address')
  return render(request,'address_list.html',{'addresses':addresses,'cart_count':cart_count}) 



def add_address_form(request):
  if not request.user.is_authenticated:
    return render('login')
  
  state_choices = AddressModel.STATE_CHOICES
  cart_count = get_cart_count(request.user)
  
  return render(request,'add_address_form.html',{'state_choices':state_choices,'cart_count':cart_count})


def edit_address_form(request):
  if not request.user.is_authenticated:
    return redirect('login')
  
  if request.method == "POST":
    state_choices = AddressModel.STATE_CHOICES
    address_id = request.POST.get('address_id',None)
    address = AddressModel.objects.filter(id=address_id).first()
    next_url = request.POST.get('next_url',None)
    next_template = request.POST.get('next_template',None)
    cart_count = get_cart_count(request.user)

    return render(request,'edit_address_form.html',{'state_choices':state_choices,'address':address,'next_url':next_url,'next_template':next_template,'cart_count':cart_count})



def set_address_as_default(request):
  if not request.user.is_authenticated:
    return redirect('login')
  if request.method == "POST":
    address_id = request.POST.get('address_id',None)
    if not address_id:
      return redirect('address_list')
    
    address = AddressModel.objects.filter(user=request.user,id=address_id).first()
    if not address:
      return redirect('address_list')
    
    AddressModel.objects.filter(user=request.user,default_address=True).update(default_address = False)
    address.default_address = True
    address.save()
    
    return redirect('address_list')

  


def delete_address(request):
  if not request.user.is_authenticated:
    return redirect('login')
  
  if request.method == 'POST':
    address_id = request.POST.get('address_id',None)
    if not address_id:
      return redirect('address_list')
    
    AddressModel.objects.filter(id=address_id).delete()
    return redirect('address_list')




def add_address(request):
  if not request.user.is_authenticated:
    return render('login')
  
  if request.method == "POST":
    form = AddAddressForm(request.POST)
    next_url = request.POST.get('next_url',None)
    next_template = request.POST.get('next_template',None)

    if form.is_valid():
      

      default_address = form.cleaned_data['default_address']
      if default_address:
        AddressModel.objects.filter(user=request.user,default_address=True).update(default_address=False)
      

      new_address = AddressModel.objects.create(user      = request.user,
                                                full_name = form.cleaned_data['full_name'],
                                                phone     = form.cleaned_data['phone'],
                                                house     = form.cleaned_data['house'],
                                                street    = form.cleaned_data['street'],
                                                city      = form.cleaned_data['city'],
                                                state     = form.cleaned_data['state'],
                                                landmark  = form.cleaned_data['landmark'],
                                                pincode   = form.cleaned_data['pincode'],
                                                default_address = True if default_address else False
                                                )
      
      if not AddressModel.objects.filter(user=request.user,default_address=True).exists():
        new_address.default_address = True
        new_address.save()

      return redirect(next_url)
    
    state_choices = AddressModel.STATE_CHOICES
    addresses     = AddressModel.objects.filter(user=request.user)
    cart_items    = CartModel.objects.filter(user_id=request.user.id)
    cart_count    = get_cart_count(request.user)
    return render(request,next_template,{'open_modal':True,'form':form,'cart_count':cart_count,'state_choices':state_choices,'cart_items':cart_items,'addresses':addresses})
      
  
def edit_address(request):
  if not request.user.is_authenticated:
    return redirect('login')
  
  if request.method == "POST":
    address_id = request.POST.get('address_id',None)
    if not address_id:
      return redirect('delivery_address_select')
    
    next_url = request.POST.get('next_url',None)
    next_template = request.POST.get('next_template',None)

    edit_form = AddAddressForm(request.POST)
    addresses = AddressModel.objects.filter(user=request.user)

    if edit_form.is_valid():
      default_address = edit_form.cleaned_data['default_address']
      if default_address:
        AddressModel.objects.filter(user=request.user,default_address=True).update(default_address=False)

      address = addresses.filter(id=address_id).first()

      address.full_name = edit_form.cleaned_data['full_name']
      address.phone     = edit_form.cleaned_data['phone']
      address.house     = edit_form.cleaned_data['house']
      address.street    = edit_form.cleaned_data['street']
      address.city      = edit_form.cleaned_data['city']
      address.state     = edit_form.cleaned_data['state']
      address.landmark  = edit_form.cleaned_data['landmark']
      address.pincode   = edit_form.cleaned_data['pincode']
      address.default_address = True if edit_form.cleaned_data['default_address'] else False

      address.save()
      return redirect(next_url)
    
    state_choices = AddressModel.STATE_CHOICES
    cart_items    = CartModel.objects.filter(user_id=request.user.id)
    cart_count    = get_cart_count(request.user)
    return render(request,next_template,{'open_modal_for':int(address_id),'edit_form':edit_form,'state_choices':state_choices,'addresses':addresses,'cart_items':cart_items,'cart_count':cart_count})
      

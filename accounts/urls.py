from django.urls import path
from accounts import views


urlpatterns=[
  path('login/',views.login, name="login"),
  path('logout/',views.logout, name="logout"),
  path('register/',views.register, name="register"),

  # User Url's
  path('user-profile/',views.user_profile, name="user_profile"),
  path('user-profile/orders/listing/',views.order_list, name="order_list"),
  path('user-profile/orders/listing/track/', views.order_track, name="order_track"),

  # Admin Url's
  path('admin-profile/',                          views.admin_profile,       name="admin_profile"),
  path('admin-profile/search_users/',views.search_users, name="search_users"),
  path('admin-profile/orders/listing/',           views.admin_order_list,    name="admin_order_list"),
  
  path('admin-profile/orders/info/<int:order_id>/',  views.admin_order_info,    name="admin_order_info"),
  path('admin-profile/orders/info/status/update/',views.admin_order_status_update, name="admin_order_status_update"),
  path('admin-profile/customers/listing/',        views.admin_customer_list, name="admin_customer_list"),
  path('admin-profile/staff/logs/', views.staff_log, name="staff_log"),
  path('admin-profile/staff/alert/list/',views.admin_alert_list, name="admin_alert_list"),
  
  


  path('user-profile/address/listing/', views.address_list ,name='address_list'),
  path('user-profile/address/listing/add/address/',views.add_address_form, name="open_add_address_form"),
  path('user-profile/address/listing/edit/address/',views.edit_address_form, name="open_edit_address_form"),
  path('user-profile/address/listing/edit/default/address/',views.set_address_as_default,name="set_as_default"),
  path('user-profile/address/listing/delete/address/',views.delete_address, name="delete_address"),

  path('add-address/',views.add_address, name='add_address'),
  path('edit-address/',views.edit_address, name="edit_address"),

]
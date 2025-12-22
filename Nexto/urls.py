from django.urls import path
from Nexto import views

urlpatterns = [
    path('',views.index,name="index"),
    path('cart/',views.cart,name="cart"),  
    path('cart/update_cart/',views.update_cart, name='update_cart'),
    
    path('contact/',views.contact,name="contact"),
    path('cobtact/submission/',views.contact_submission, name='contact_submission'),

    path('testimonial/',views.testimonial,name="testimonial"),

    path('checkout/',views.checkout,name="checkout"),
    path('checkout/address/select/',views.delivery_address_select,name='delivery_address_select'),
    
    path('checkout/start-payment/cod/verification/<int:payment_id>/',views.cod_payment, name="cod_payment"),
    path('checkout/start-payment/',views.start_payment, name="start_payment"),
    path('checkout/start-payment/verification/',views.verify_payment, name="verify_payment"),
    path('checkout/start-payment/verification/success/<int:payment_id>/',views.payment_success, name="payment_success"),
    path('checkout/start-payment/verification/failed/<int:payment_id>/',views.payment_failed, name="payment_failed"),

    path('shop/',views.shop,name="shop"),
    path('shop_detail/<int:product_id>/',views.shop_detail,name="shop_detail"),
]

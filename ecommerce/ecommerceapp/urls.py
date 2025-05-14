from django.urls import path
from ecommerceapp import views
from authcart.views import profile_view

urlpatterns = [
    path('', views.index, name="home"),            
    path('home/', views.index, name="index"),   
    path('contact/', views.contact, name="contact"),
    path('about/', views.about, name="about"), 
    path('profile/', profile_view, name='profile'),
    path('product/<int:id>/', views.view_product, name='product_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('cart-count/', views.cart_count, name='cart_count'),
    path('order-success/', views.order_success, name='order_success'),
    path('checkout-summary/', views.checkout_summary, name='checkout_summary'),
    path('payment/', views.payment_view, name='payment'), 
    path('payment-status/', views.payment_status, name='payment_status'),
    path('tracker/', views.tracker, name='tracker'),
    path('myorder/', views.myorder, name='myorder'),
    path('payment-success/', views.payment_success, name='payment_success'),

]



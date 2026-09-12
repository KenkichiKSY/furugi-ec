from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartDetailView.as_view(), name='cart_detail'),
    path('cart/add/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/', views.payment_success, name='payment_success'),
    path('orders/', views.OrderHistoryView.as_view(), name='order_history'),
]
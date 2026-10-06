from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/review/',views.add_review,name='add_review'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('cart/increase/<int:cart_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:cart_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('cart/remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('cancel-order/<int:order_id>/',views.cancel_order,name='cancel_order'),
    path('seller/', views.seller_home, name='seller_home'),
    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller-dashboard/add-product/', views.add_product, name='add_product'),
    path('seller-dashboard/edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('seller-dashboard/delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('seller-dashboard/orders/', views.seller_orders, name='seller_orders'),
    path('seller-dashboard/update-order-status/<int:order_id>/',views.update_order_status,name='update_order_status'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('buyer/login/', views.buyer_login, name='buyer_login'),
path('buyer/register/', views.buyer_register, name='buyer_register'),

path('seller/login/', views.seller_login, name='seller_login'),
path('seller/register/', views.seller_register, name='seller_register'),
]
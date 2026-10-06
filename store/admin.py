from django.contrib import admin

# Register your models here.
from.models import Product, Cart, Order, Review, BuyerAccount, SellerAccount

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(BuyerAccount)
admin.site.register(SellerAccount)

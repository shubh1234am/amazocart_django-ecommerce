from django.contrib import admin
from .models import Contact, Product, Order
from .models import Payment

# Register Contact and Product models
admin.site.register(Contact)
admin.site.register(Product)

# Customize Order model display in the admin panel

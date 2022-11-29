from django.contrib import admin
from .models import Products,Outlets,Orders
# Register your models here.
admin.site.register(Products)
admin.site.register(Outlets)
admin.site.register(Orders)
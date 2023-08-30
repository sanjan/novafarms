from django.contrib import admin
from .models import HoneyType, Brand, Pallet, Container, Lid, Carton, Label, TopInsert, Product, Supplier


admin.site.site_header = "Nova Farms Administration"

admin.site.register(HoneyType)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(Container)
admin.site.register(Lid)
admin.site.register(Label)
admin.site.register(Carton)
admin.site.register(Pallet)
admin.site.register(TopInsert)
admin.site.register(Supplier)

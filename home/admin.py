from django.contrib import admin
from .models import HoneyType, Brand, Config

admin.site.site_header = "NovaFarms Administration"

admin.site.register(Config)
admin.site.register(HoneyType)
admin.site.register(Brand)

# admin.site.register(Product)
# admin.site.register(Container)
# admin.site.register(Lid)
# admin.site.register(Label)
# admin.site.register(Carton)
# admin.site.register(Pallet)
# admin.site.register(TopInsert)
# admin.site.register(Supplier)

from django.contrib import admin
from .models import HoneyType, Brand, Pallet, Container, Lid, Carton, Label, TopInsert


admin.site.site_header = "Nova Farms Administration"

admin.site.register(HoneyType)
admin.site.register(Brand)
admin.site.register(Pallet)
admin.site.register(Container)
admin.site.register(Lid)
admin.site.register(Carton)
admin.site.register(Label)
admin.site.register(TopInsert)
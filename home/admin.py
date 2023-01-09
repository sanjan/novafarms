from django.contrib import admin
from .models import Beekeeper, Order, OrderItem, Honey


admin.site.site_header = "Nova Farms Administration"

class BeekeeperAdmin(admin.ModelAdmin):
    list_display = ('supplier_name', 'supplier_number', 'suburb','state', 'email')
    list_filter = ['state', 'suburb']
    
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'bee_keeper', 'date', 'gross_total_weight', 'ibc_weight', 'net_weight', 'honey_levy', 'unit_price', 'total_price', 'immediate_payment')
    list_filter = ('bee_keeper', 'date')
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'type', 'gross_weight')
    list_filter = [ 'order']
    
# Register your models here.
admin.site.register(Beekeeper, BeekeeperAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Honey)

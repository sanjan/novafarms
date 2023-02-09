from django.contrib import admin
from .models import Beekeeper, Order, OrderItem, HoneyType, Batch


admin.site.site_header = "Nova Farms Administration"

class BeekeeperAdmin(admin.ModelAdmin):
    list_display = ('name', 'supplier_number', 'suburb', 'state', 'email')
    list_filter = ['state', 'suburb']
    
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'bee_keeper', 'date', 'gross_total_weight', 'ibc_total_weight', 'net_weight', 'honey_levy', 'unit_price', 'total_price', 'payment_term')
    list_filter = ('bee_keeper', 'date')
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id','ibc_weight', 'gross_weight')
    list_filter = ['order']

class BatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch_number', 'batch_date', 'expiry_date', 'brand', 'bottle_type' )
    list_filter = ['brand']
    
# Register your models here.
admin.site.register(Beekeeper, BeekeeperAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(HoneyType)
admin.site.register(Batch, BatchAdmin)
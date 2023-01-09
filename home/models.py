import decimal
from django.db import models
from django.db.models import Sum
from django.utils import timezone

# Create your models here.
STATE = (
    ('ACT', 'ACT'),
    ('NSW', 'NSW'),
    ('NT', 'NT'),
    ('QLD', 'QLD'),
    ('SA', 'SA'),
    ('TAS', 'TAS'),
    ('VIC', 'VIC'),
    ('WA', 'WA'),
)

HONEY_LEVY_MULTIPLIER = decimal.Decimal('0.046')


class Honey(models.Model):
    type = models.CharField(max_length=100,null=True, blank=True)
    
    def __str__(self) -> str:
        return self.type
class Beekeeper(models.Model):
    supplier_name = models.CharField(max_length=100, unique=True)
    supplier_number = models.CharField(max_length=100,null=True, blank=True)
    ibc_identification = models.CharField(max_length=100,null=True, blank=True, verbose_name='IBC identification')
    unit_number = models.CharField(max_length=10, blank=True, null=True)
    street_number = models.CharField(max_length=10,blank=True,null=True)
    address_line_1 = models.CharField(max_length=100,blank=True, null=True)
    address_line_2 = models.CharField(max_length=100,blank=True,null=True)
    suburb = models.CharField(max_length=50,blank=True,null=True)
    state = models.CharField(max_length=3, choices=STATE)
    post_code = models.CharField(max_length=4)
    contact_number = models.CharField(max_length=20,blank=True,null=True)
    abn = models.CharField(max_length=100,blank=True, verbose_name ='ABN')
    email = models.EmailField(max_length=100,blank=True, verbose_name ='e-mail')
    
    class Meta:
        ordering = ("supplier_name",)
    
    def __str__(self) -> str:
        return self.supplier_name
    

class Order(models.Model):
    bee_keeper = models.ForeignKey(Beekeeper, on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=10, unique=True, null=True, editable=False)
    gross_total_weight = models.DecimalField(default=0.00, decimal_places=2,  editable=False, max_digits=10)
    ibc_weight = models.DecimalField(default=0.00, decimal_places=2,max_digits=10 )
    net_weight = models.DecimalField(default=0.00, decimal_places=2, editable=False, max_digits=10)
    honey_levy = models.DecimalField(default=0.00, decimal_places=2, editable=False, max_digits=10)
    unit_price = models.DecimalField(default=0.00, decimal_places=2,max_digits=10 )
    total_price = models.DecimalField(default=0.00, decimal_places=2, editable=False,max_digits=10)
    immediate_payment = models.BooleanField(default=True)
    date = models.DateField(default=timezone.now)
    
    def __str__(self) -> str:
        return f'{self.order_number} - {self.bee_keeper}'
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            order_items = self.order_items.all()
            self.gross_total_weight = order_items.aggregate(Sum('gross_weight'))['gross_weight__sum'] if order_items.exists() else 0.0
            if self.ibc_weight > 0.0 and self.gross_total_weight > 0.0 and self.ibc_weight < self.gross_total_weight:
                self.net_weight = self.gross_total_weight - self.ibc_weight
            if self.net_weight > 0.0:
                self.honey_levy = self.net_weight * HONEY_LEVY_MULTIPLIER
            if self.unit_price > 0.0 and self.honey_levy > 0.0:
                self.total_price = (self.net_weight * self.unit_price) + self.honey_levy
        if self.pk is None or self.order_number is None:
            id_length = len(str(self.id))
            code_length = 7 - id_length
            zeroes = "".join("0" for i in range(code_length))
            self.order_number = f"INV{zeroes}{self.id}"
            self.save()
                
        super().save(*args, **kwargs)

    
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, related_name='order_items')
    type = models.ForeignKey(Honey, on_delete=models.PROTECT)
    gross_weight = models.DecimalField(default=0.00, decimal_places=2,max_digits=10 )
    
    def __str__(self) -> str:
        return f'{self.order.id} - {self.type}({self.gross_weight} kg)'
    
    def save(self,  *args, **kwargs):   
        super().save(*args, **kwargs)
        self.order.save()
        
        
        
    
    
    
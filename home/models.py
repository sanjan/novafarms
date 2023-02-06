import decimal
from django.db import models
from django.db.models import Sum
from django.utils import timezone
import qrcode
import datetime
from django.conf import settings

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

BATCH_STATE = (
    ('New', 'New'),
    ('Processing', 'Processing'),
    ('Complete', 'Complete'),
    
)

PAYMENT_TERMS = (
    ('Immediate', 'Immediate'),
    ('30 Days', '30 Days'),
)

HONEY_LEVY_MULTIPLIER = decimal.Decimal('0.046')


class HoneyType(models.Model):
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
    abn = models.CharField(max_length=100,blank=True,null=True, verbose_name ='ABN')
    email = models.EmailField(max_length=100,blank=True, verbose_name ='e-mail')
    account_name = models.CharField(max_length=100,blank=True,null=True)
    bsb = models.CharField(max_length=100,blank=True,null=True, verbose_name ='BSB')
    account_number =  models.CharField(max_length=100,blank=True,null=True)
    
    class Meta:
        ordering = ("supplier_name",)
    
    def __str__(self) -> str:
        return self.supplier_name
    

class Order(models.Model):
    bee_keeper = models.ForeignKey(Beekeeper, on_delete=models.PROTECT)
    order_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    gross_total_weight = models.DecimalField(default=0.00, decimal_places=2,  editable=False, max_digits=10, verbose_name ='Gross Weight')
    ibc_total_weight = models.DecimalField(default=0.00, decimal_places=2, editable=False, max_digits=10,  verbose_name ='IBC/Drum Weight')
    net_weight = models.DecimalField(default=0.00, decimal_places=2, editable=False, max_digits=10)
    honey_levy = models.DecimalField(default=0.00, decimal_places=2, editable=False, max_digits=10)
    unit_price = models.DecimalField(default=0.00, decimal_places=2, max_digits=10 )
    total_price = models.DecimalField(default=0.00, decimal_places=2, editable=False,max_digits=10)
    payment_term = models.CharField(max_length=20, choices=PAYMENT_TERMS)
    date = models.DateField(default=timezone.now)
    qrcode = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ("-id",)
    
    def __str__(self) -> str:
        return f'{self.order_number} - {self.bee_keeper}'
   
    def save(self, *args, **kwargs):
        if self.pk is not None:
            order_items = self.order_items.all()
            self.gross_total_weight = order_items.aggregate(Sum('gross_weight'))['gross_weight__sum'] if order_items.exists() else 0.0
            self.ibc_total_weight = order_items.aggregate(Sum('ibc_weight'))['ibc_weight__sum'] if order_items.exists() else 0.0
            if self.ibc_total_weight > 0.0 and self.gross_total_weight > 0.0 and self.ibc_total_weight < self.gross_total_weight:
                self.net_weight = self.gross_total_weight - self.ibc_total_weight
            if self.net_weight > 0.0:
                self.honey_levy = self.net_weight * HONEY_LEVY_MULTIPLIER
            if self.unit_price > 0.0 and self.honey_levy > 0.0:
                self.total_price = (self.net_weight * self.unit_price) + self.honey_levy
            qc = qrcode.make(f'http://localhost:8000/order-details/{self.id}/')
            qc_path = f'{settings.MEDIA_ROOT}/order_qr_codes/qr_code_{self.id}.png'
            qc_url =  f'{settings.MEDIA_URL}order_qr_codes/qr_code_{self.id}.png'
            qc.save(qc_path)
            self.qrcode = qc_url
            

        super().save(*args, **kwargs)
        self.set_order_number()
        
    
    def set_order_number(self):
        if not self.order_number:
            id_length = len(str(self.id))
            code_length = 7 - id_length
            zeroes = "".join("0" for i in range(code_length))
            order_number = f"INV{zeroes}{self.id}"
            order = Order.objects.get(id=self.id)
            order.order_number = order_number
            order.save()
            
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    ibc_weight = models.DecimalField(default=0.00, decimal_places=2, max_digits=10 )
    gross_weight = models.DecimalField(default=0.00, decimal_places=2, max_digits=10 )
    net_weight = models.DecimalField(default=0.00, decimal_places=2, max_digits=10, null=True )
    honey_types = models.ManyToManyField(HoneyType)
    nv_ibc = models.CharField(max_length=100,null=True, blank=True, verbose_name='Nova IBC')
    used = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        ht = ', '.join([h.type for h in self.honey_types.all() ])
        return f'{self.order.date} {self.order.bee_keeper} {self.gross_weight-self.ibc_weight}kg ({ht})'
    
    def save(self, *args, **kwargs):
        self.net_weight = self.gross_weight - self.ibc_weight
        super().save(*args, **kwargs)
        

class Batch(models.Model):
    batch_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField(default= datetime.date.today() + datetime.timedelta(days=365*5))
    batch_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    source_containers = models.ManyToManyField(OrderItem)
    brand = models.CharField(max_length=100,blank=True, null=True)
    product_name = models.CharField(max_length=100,blank=True, null=True)
    bottle_type = models.CharField(max_length=100,blank=True, null=True)
    unit_weight = models.IntegerField(default=0 )
    total_weight = models.DecimalField(default=0.00, decimal_places=2, max_digits=10 )
    number_made = models.PositiveIntegerField(null=True)
    max_possible = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=BATCH_STATE, default='New')
    qrcode_url = models.CharField(max_length=100, null=True, blank=True)
    qrcode_path = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        ordering = ("-id",)
    
    def __str__(self) -> str:
        return f'{self.batch_number} - {self.brand} - {self.bottle_type}'
   
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.set_batch_number()
        self.gen_qr_code()
    
    def set_batch_number(self):
        if not self.batch_number:
            id_length = len(str(self.id))
            code_length = 7 - id_length
            zeroes = "".join("0" for i in range(code_length))
            batch_number = f"NVF{zeroes}{self.id}"
            batch = Batch.objects.get(id=self.id)
            batch.batch_number = batch_number
            batch.save()
    
    def gen_qr_code(self):
        if not self.qrcode_url:
            qc = qrcode.make(f'http://localhost:8000/batch-details/{self.batch_number}/')
            file_path = f'/batch_qr_codes/batch_qr_code_{self.batch_number}.png'
            qc_path = f'{settings.MEDIA_ROOT}{file_path}'
            qc_url =  f'{settings.MEDIA_URL}{file_path}'
            qc.save(qc_path)
            batch = Batch.objects.get(id=self.id)
            batch.qrcode_url = qc_url
            batch.qrcode_path = qc_path
            batch.save()
            
            
     
     
        

    
    
        
        
    
    
    
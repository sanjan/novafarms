
from django.db import models
from django.db.models import Sum
from django.utils import timezone
import qrcode
import datetime
import io
from django.core.files.base import ContentFile
from shortuuid.django_fields import ShortUUIDField
from django_countries.fields import CountryField
from django.conf import settings

# Create your models here.
STATE = (
    ('ACT', 'Australian Capital Territory'),
    ('NSW', 'New South Wales'),
    ('NT', 'Northern Territory'),
    ('QLD', 'Queensland'),
    ('SA', 'South Australia'),
    ('TAS', 'Tasmania'),
    ('VIC', 'Victoria'),
    ('WA', 'Western Australia'),
)

PRODUCTION_STATUS = (
    ('New', 'New'),
    ('Processing', 'Processing'),
    ('Paused', 'Paused'),
    ('Complete', 'Complete'),
)

PAYMENT_TERMS = (
    ('Immediate', 'Immediate'),
    ('30 Days', '30 Days'),
)

HONEY_CONTAINER_TYPES = (
    ('Jar','Jar'),
    ('Squeeze Bottle','Squeeze Bottle'),
    ('Pail','Pail'),
)
LID_TYPES = (
    ('Jar Lid','Jar Lid'),
    ('Squeeze Lid','Squeeze Lid'),
    ('Squeeze Tip','Squeeze Tip'),
    ('Pail Lid','Pail Lid'),
    
)

LID_CONTAINER_COLORS = (
    ('Clear','Clear'),
    ('Yellow','Yellow'),
    ('Black','Black'),
    ('Dark Brown','Dark Brown'),
    ('White','White'),
)



class Config(models.Model):
    last_updated = models.DateField(default=timezone.now)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    
    def __str__(self) -> str:
        return f'{self.name}: {self.value} ({self.last_updated})'

class HoneyType(models.Model):
    type = models.CharField(max_length=100,null=True, blank=True)
    
    def __str__(self) -> str:
        return self.type

class Brand(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)
    def __str__(self) -> str:
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=50, null=True)
    customer_number = models.CharField(max_length=100,null=True, blank=True)
    unit_number = models.CharField(max_length=10, blank=True, null=True)
    street_number = models.CharField(max_length=10,blank=True,null=True)
    address_line_1 = models.CharField(max_length=100,blank=True, null=True)
    address_line_2 = models.CharField(max_length=100,blank=True,null=True)
    suburb = models.CharField(max_length=50,blank=True,null=True)
    state = models.CharField(max_length=3, choices=STATE, blank=True,null=True)
    country = CountryField(blank_label="select country")
    post_code = models.CharField(max_length=4)
    contact_number = models.CharField(max_length=20,blank=True,null=True)
    email = models.EmailField(max_length=100,blank=True, verbose_name ='e-mail')
    class Meta:
        ordering = ("name",)
    
    def __str__(self) -> str:
        return self.name

class CustomerOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    order_number = ShortUUIDField(length=16,max_length=16,prefix="so_",alphabet="abcdefhkmnrstuvwxz123456789_",)
    unit_price = models.DecimalField(default=0.00, decimal_places=2, max_digits=10 )
    total_price = models.DecimalField(default=0.00, decimal_places=2, editable=False,max_digits=10)
    payment_term = models.CharField(max_length=20, choices=PAYMENT_TERMS)
    date = models.DateField(auto_now_add=True)
    qrcode = models.ImageField(upload_to='supplier_order_qr_codes',blank=True,null=True)
    qr_pointer = models.CharField(max_length=300, unique=True, null=True, blank=True)
    class Meta:
        ordering = ("-id",)
    
    def __str__(self) -> str:
        return f'{self.order_number} - {self.supplier}'
   
    def save(self, *args, **kwargs):
        if self.pk is not None:
            honey_stock = self.honey_stock.all()
            self.gross_total_weight = honey_stock.aggregate(Sum('gross_weight'))['gross_weight__sum'] if honey_stock.exists() else 0.0
            self.ibc_total_weight = honey_stock.aggregate(Sum('ibc_weight'))['ibc_weight__sum'] if honey_stock.exists() else 0.0
            if self.ibc_total_weight > 0.0 and self.gross_total_weight > 0.0 and self.ibc_total_weight < self.gross_total_weight:
                self.net_total_weight = self.gross_total_weight - self.ibc_total_weight
            if self.net_total_weight > 0.0:
                self.honey_levy = self.net_total_weight * settings.HONEY_LEVY_MULTIPLIER
            if self.unit_price > 0.0 and self.honey_levy > 0.0 and self.total_price == 0.0:       
                self.total_price = (self.net_total_weight * self.unit_price) + self.honey_levy
        
        if self.qr_pointer is not None:
            qr_file_name = f'so_{self.order_number}.png'
            qr = qrcode.QRCode(version=2)
            qr.add_data(self.qr_pointer)
            qr.make(fit=True)
            img = qr.make_image()
            buff = io.BytesIO()
            img.save(buff)
            self.qrcode.save(qr_file_name, ContentFile(buff.getvalue()), save=False)
            

        super().save(*args, **kwargs)
        
class Pallet(models.Model):
    pallet_name = models.CharField(max_length=100,null=True, blank=True)
    pallet_number = models.CharField(max_length=100,null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    width = models.IntegerField(default=0)
    length = models.IntegerField(default=0)
    quantity =  models.IntegerField(default=0)
    capacity_cartons = models.IntegerField(default=0)
    layout = models.FileField(upload_to='pallet_layouts/',blank=True,null=True)
    last_updated =  models.DateField(auto_now=True)
    
    def __str__(self) -> str:
        return f'{self.pallet_name} - {self.customer.name} - {self.pallet_number}'

class Container(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)
    brand = models.ForeignKey(Brand, null=True,blank=True, on_delete=models.PROTECT)
    type = models.CharField(max_length=20, choices=HONEY_CONTAINER_TYPES)
    quantity =  models.IntegerField(default=0)
    capacity =  models.IntegerField(default=0)
    color = models.CharField(max_length=20, choices=LID_CONTAINER_COLORS)
    last_updated =  models.DateField(auto_now=True)

class Lid(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)
    brand = models.ForeignKey(Brand, null=True,blank=True, on_delete=models.PROTECT)
    type = models.CharField(max_length=20, choices=LID_TYPES)
    quantity =  models.IntegerField(default=0)
    color = models.CharField(max_length=20, choices=LID_CONTAINER_COLORS)
    last_updated =  models.DateField(auto_now=True)

class Carton(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.PROTECT)
    capacity =  models.IntegerField(default=0)
    quantity =  models.IntegerField(default=0)
    last_updated =  models.DateField(auto_now=True)

class Label(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.PROTECT)
    quantity =  models.IntegerField(default=0)
    last_updated =  models.DateField(auto_now=True)
    
class TopInsert(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)
    dimensions = models.CharField(max_length=100,null=True, blank=True)
    quantity =  models.IntegerField(default=0)
    last_updated =  models.DateField(auto_now=True)
    
class Supplier(models.Model):
    name = models.CharField(max_length=50, null=True)
    supplier_number = models.CharField(max_length=100,null=True, blank=True)
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
        ordering = ("name",)
    
    def __str__(self) -> str:
        return self.name
    
class SupplierOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    order_number = ShortUUIDField(length=16,max_length=16,prefix="so_",alphabet="abcdefhkmnrstuvwxz123456789",)
    gross_total_weight = models.DecimalField(default=0.00, decimal_places=2,  editable=False, max_digits=10, verbose_name ='Gross Weight')
    ibc_total_weight = models.DecimalField(default=0.00, decimal_places=2, editable=False, max_digits=10,  verbose_name ='IBC/Drum Weight')
    net_total_weight = models.DecimalField(default=0.00, decimal_places=2, editable=False, max_digits=10)
    honey_levy = models.DecimalField(default=0.00, decimal_places=2, editable=False, max_digits=10)
    unit_price = models.DecimalField(default=0.00, decimal_places=2, max_digits=10 )
    total_weight_price = models.DecimalField(default=0.00, decimal_places=2, editable=False,max_digits=10)
    total_price = models.DecimalField(default=0.00, decimal_places=2, editable=False,max_digits=10)
    payment_term = models.CharField(max_length=20, choices=PAYMENT_TERMS)
    date = models.DateField(auto_now_add=True)
    qrcode = models.ImageField(upload_to='supplier_order_qr_codes',blank=True,null=True)
    qr_pointer = models.CharField(max_length=300, unique=True, null=True, blank=True)
    class Meta:
        ordering = ("-id",)
    
    def __str__(self) -> str:
        return f'{self.order_number} - {self.supplier}'
   
    def save(self, *args, **kwargs):
        if self.pk is not None:
            honey_stock = self.honey_stock.all()
            self.gross_total_weight = honey_stock.aggregate(Sum('gross_weight'))['gross_weight__sum'] if honey_stock.exists() else 0.0
            self.ibc_total_weight = honey_stock.aggregate(Sum('ibc_weight'))['ibc_weight__sum'] if honey_stock.exists() else 0.0
            if self.ibc_total_weight > 0.0 and self.gross_total_weight > 0.0 and self.ibc_total_weight < self.gross_total_weight:
                self.net_total_weight = self.gross_total_weight - self.ibc_total_weight
            if self.net_total_weight > 0.0:
                self.honey_levy = self.net_total_weight * settings.HONEY_LEVY_MULTIPLIER
                self.total_weight_price = self.net_total_weight * self.unit_price
            if self.unit_price > 0.0 and self.honey_levy > 0.0 and self.total_price == 0.0:      
                self.total_price = self.total_weight_price + self.honey_levy
        
        if self.qr_pointer is not None:
            qr_file_name = f'so_{self.order_number}.png'
            qr = qrcode.QRCode(version=2)
            qr.add_data(self.qr_pointer)
            qr.make(fit=True)
            img = qr.make_image()
            buff = io.BytesIO()
            img.save(buff)
            self.qrcode.save(qr_file_name, ContentFile(buff.getvalue()), save=False)
            

        super().save(*args, **kwargs)
    #     self.set_order_number()
        
    
    # def set_order_number(self):
    #     if not self.order_number:
    #         id_length = len(str(self.id))
    #         code_length = 7 - id_length
    #         zeroes = "".join("0" for i in range(code_length))
    #         order_number = f"sup_ord_{zeroes}{self.id}"
    #         order = SupplierOrder.objects.get(id=self.id)
    #         order.order_number = order_number
    #         order.save()
            
class Production(models.Model):
    packing_date = models.DateField(default=timezone.now)
    production_code = ShortUUIDField(length=16,max_length=16,prefix="p_",alphabet="abcdefhkmnrstuvwxz123456789_",)
    order = models.ForeignKey(CustomerOrder, on_delete=models.SET_NULL, related_name='product', null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    pallet = models.ForeignKey(Pallet, on_delete=models.PROTECT, null=True, blank=True)
    container = models.ForeignKey(Container, on_delete=models.PROTECT)
    lid = models.ForeignKey(Lid, on_delete=models.PROTECT)
    carton  = models.ForeignKey(Carton, on_delete=models.PROTECT)
    label = models.ForeignKey(Label, on_delete=models.PROTECT)
    top_insert = models.ForeignKey(TopInsert, on_delete=models.PROTECT, null=True, blank=True)
    product_name = models.CharField(max_length=100,blank=True, null=True)
    bottle_type = models.CharField(max_length=100,blank=True, null=True)
    total_weight = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    units_made = models.PositiveIntegerField(null=True)
    units_requested = models.PositiveIntegerField(null=True)
    status = models.CharField(max_length=20, choices=PRODUCTION_STATUS, default='New')
    product_image = models.ImageField(upload_to='production_images',blank=True,null=True)
        
    def save(self, *args, **kwargs):           
        super().save(*args, **kwargs)
        
class Batch(models.Model):
    batch_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()
    batch_number = ShortUUIDField(length=16,max_length=16,prefix="b_",alphabet="abcdefhkmnrstuvwxz123456789",)
    production = models.ForeignKey(Production, on_delete=models.SET_NULL, related_name='batch', null=True)
    qrcode = models.ImageField(upload_to='batch_qr_codes',blank=True,null=True)
    qr_pointer = models.CharField(max_length=300, unique=True, null=True, blank=True)
    
    class Meta:
        ordering = ("-id",)
    
    def __str__(self) -> str:
        return f'{self.batch_number} - {self.brand} - {self.bottle_type}'
   
    def save(self, *args, **kwargs):
        if self.qr_pointer is not None:
            qr_file_name = f'batch_{self.batch_number}.png'
            qr = qrcode.QRCode(version=2)
            qr.add_data(self.qr_pointer)
            qr.make(fit=True)
            img = qr.make_image()
            buff = io.BytesIO()
            img.save(buff)
            self.qrcode.save(qr_file_name, ContentFile(buff.getvalue()), save=False)
            
        super().save(*args, **kwargs)
    #     self.set_batch_number()
    
    # def set_batch_number(self):
    #     if not self.batch_number:
    #         id_length = len(str(self.id))
    #         code_length = 7 - id_length
    #         zeroes = "".join("0" for i in range(code_length))
    #         batch_number = f"nvf_batch_{zeroes}{self.id}"
    #         batch = Batch.objects.get(id=self.id)
    #         batch.batch_number = batch_number
    #         batch.save()
            
class HoneyStock(models.Model):
    order = models.ForeignKey(SupplierOrder, on_delete=models.CASCADE, related_name='honey_stock', blank=True, null=True)
    stock_id = ShortUUIDField(length=16,max_length=16,prefix="h_",alphabet="abcdefhkmnrstuvwxz123456789")
    ibc_weight = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    gross_weight = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    net_weight = models.DecimalField(default=0.00, decimal_places=2, max_digits=10, null=True)
    honey_types = models.ManyToManyField(HoneyType)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, related_name='batch', null=True, blank=True)
    nova_ibc = models.CharField(max_length=100,null=True, blank=True, verbose_name='Nova IBC')
    supplier_ibc = models.CharField(max_length=100,null=True, blank=True, verbose_name='Supplier IBC')
    date_received = models.DateField(auto_now_add=True)
    
    def __str__(self) -> str:
        # ht = ', '.join([h.type for h in self.honey_types.all() ])
        return f'{self.order.date} {self.order.supplier} {self.net_weight}kg ()'
    
    def save(self, *args, **kwargs):
        self.net_weight = self.gross_weight - self.ibc_weight
        super().save(*args, **kwargs)   
            
    
    
    
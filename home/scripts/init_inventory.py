from home.models import Carton, TopInsert, Lid, Container, Label, Product
import csv
import requests
from tempfile import NamedTemporaryFile
from django.core.files import File


def insert_image(product, image_url):
    if image_url != '':
        r = requests.get(image_url)
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(r.content)
        img_temp.flush()
        with open(img_temp.name, mode="rb") as f:
            product.image = File(f, name="image")
            product.save()
    
def run(*args):
    with open(args[0]) as file:
        reader = csv.reader(file)
        next(reader)
        # Product.objects.all().delete()
        Carton.objects.all().delete()
        TopInsert.objects.all().delete()
        Lid.objects.all().delete()
        Container.objects.all().delete()
        Label.objects.all().delete()
        
        for row in reader:
            name = row[0]
            quantity = int(row[9]) if row[9] is not None else 0
            category = row[16]
            image_url = row[21] if row[21] is not None else ''
            print(f"{name}, {quantity}, {category}, {image_url}")
            
            if category == "Labels":
                label = Label.objects.create(
                    name = name,
                    quantity = quantity,
                )
                insert_image(label, image_url)
                
            elif category == "Bottles/Jars":
                container = Container.objects.create(
                    name = name,
                    quantity = quantity,
                )
                insert_image(container, image_url)
                
            elif category == "Cartons":
                carton = Carton.objects.create(
                    name = name,
                    quantity = quantity,
                )
                insert_image(carton, image_url)
            
            elif category == "Lids":
                lid = Lid.objects.create(
                    name = name,
                    quantity = quantity,
                )
                insert_image(lid, image_url)
                
            elif category == "Top Inserts":
                top_insert = TopInsert.objects.create(
                    name = name,
                    quantity = quantity,
                )
                insert_image(top_insert, image_url)

                    
              

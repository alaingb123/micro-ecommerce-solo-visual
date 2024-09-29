# Create your models here.


from django.db import models
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from carro.carro import Carro
from products.models import Product
from django.core.exceptions import PermissionDenied
from django.core.validators import EmailValidator,RegexValidator

from django.db import models
from django.conf import settings
from django.core.validators import EmailValidator, RegexValidator
# Create your models here.



class SolicitudZelle(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En espera'),
        ('accepted', 'Aceptada'),
        ('canceled', 'Cancelada'),
    ]
    ENTREGA_CHOICES = [
        ('pending', 'En espera'),
        ('onway', 'En camino'),
        ('accepted', 'Entregada'),
        ('canceled', 'Cancelada'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    products = models.ManyToManyField(Product, related_name='purchases')
    email = models.EmailField(validators=[EmailValidator])
    file = models.FileField(upload_to='purchase_files')
    phone = models.CharField(max_length=15, validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')])
    payment_verification_code = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Campo para la cantidad de dinero
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Campo para el estado de la solicitud
    entrega = models.CharField(max_length=10, choices=ENTREGA_CHOICES, default='pending')  # Campo para el estado de la solicitud

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk} - {self.user.username}"


    def guardar_producto(self,product,quantity,solicitud):

        SolicitudZelleItem.objects.create(
            solicitud=solicitud,
            product=product,
            quantity=quantity
        )

    def accept(self):
        for product in self.products.all():
            object = get_object_or_404(Product, pk=product.pk)
            solicitud_items = SolicitudZelleItem.objects.filter(solicitud=self,product=product)

            try:
                for solicitud_item in solicitud_items:
                    object.supply = object.supply - solicitud_item.quantity
                object.save()
            except:
                return HttpResponse("No hay sufuciente productos para esta solicitud")

        self.status = 'accepted'
        self.save()


    def cancel(self):
        self.status = 'canceled'
        self.save()



class SolicitudZelleItem(models.Model):
    solicitud = models.ForeignKey(SolicitudZelle, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"id:{self.pk} - Products:{self.product.name} - {self.quantity}"


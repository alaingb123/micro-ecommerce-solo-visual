from django.db import models

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from carro.carro import Carro
from extra.models import Destinatario, Municipio
from products.models import Product
from django.core.exceptions import PermissionDenied
from django.core.validators import EmailValidator,RegexValidator
import uuid

from django.conf import settings
from django.core.validators import EmailValidator, RegexValidator
# Create your models here.
import string
import random


def generate_unique_handle():
    while True:
        handle = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        if not Purchase.objects.filter(handle=handle).exists():
            return handle




class Purchase(models.Model):
    ENTREGA_CHOICES = [
        ('pending', 'En espera'),
        ('onway', 'En camino'),
        ('accepted', 'Entregada'),
        ('canceled', 'Cancelada'),
    ]
    handle = models.CharField(max_length=6, unique=True, default=generate_unique_handle, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product, related_name='pedidos_stripe')
    completed = models.BooleanField(default=False)
    stripe_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)  # Campo para la cantidad de dinero
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    entrega = models.CharField(max_length=10, choices=ENTREGA_CHOICES,
                               default='pending')  # Campo para el estado de la solicitud




    # # Almacenar una "instantánea" de los datos del destinatario en el momento de la venta
    nombre = models.CharField(max_length=100,blank=True, null=True)
    apellidos = models.CharField(max_length=150,default="")
    telefono = models.CharField(max_length=20,blank=True, null=True)
    carnet_de_identidad = models.CharField(max_length=11, blank=True, null=True)  # Opcional
    correo_electronico = models.EmailField(blank=True, null=True)  # Opcional
    direccion = models.CharField(max_length=255,default="")
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE,blank=True, null=True)  # Selector de municipio
    instrucciones_entrega = models.TextField(blank=True, null=True)

    def guardar_producto(self,product,quantity,purchase):

        SolicitudStripeItem.objects.create(
            solicitud=purchase,
            product=product,
            quantity=quantity
        )

    def __str__(self):
        return f"{self.pk} - {self.user.username}"


# NEcesidad de crear un campo id que contenga letras
class SolicitudStripeItem(models.Model):
    handle = models.CharField(max_length=6, unique=True, default=generate_unique_handle, editable=False)
    solicitud = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # # Almacenar una "instantánea" de los datos del producto en el momento de la venta
    product_name_snapshot = models.CharField(max_length=120,default=product.name)
    product_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)

    def save(self, *args, **kwargs):
        self.product_name_snapshot = self.product.name
        self.product_price_snapshot = self.product.price
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"id:{self.pk} - Products:{self.product.name} - {self.quantity}"




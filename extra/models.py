from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from django.contrib.auth.models import  User

from products.models import Product


# Create your models here.

class Municipio(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Destinatario(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)
    carnet_de_identidad = models.CharField(max_length=11, blank=True, null=True)  # Opcional
    correo_electronico = models.EmailField(blank=True, null=True)  # Opcional
    direccion = models.CharField(max_length=255)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)  # Selector de municipio
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario de Django
    instrucciones_entrega = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"








def crear_municipios_iniciales(sender, **kwargs):
    if kwargs['app_config'].name == 'extra':
        municipios_iniciales = [
            "Centro Habana",
            "Cerro",
            "Plaza de la Revolución",
            "La Habana Vieja",
            "Arroyo Naranjo",
            "Boyeros",
            "Cotorro",
            "Diez de Octubre",
            "Guanabacoa",
            "Habana del Este",
            "La Lisa",
            "Marianao",
            "Playa",
            "Regla",
            "San Miguel del Padrón",
            "Santa Cruz del Norte",
            "Santa Fe"
        ]
        for nombre in municipios_iniciales:
            Municipio.objects.get_or_create(nombre=nombre)


post_migrate.connect(crear_municipios_iniciales, sender=apps.get_app_config('extra'))


class Promocion(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to="promociones/", blank=True, null=True)
    imagen_peque = models.ImageField(upload_to="promociones/", blank=True, null=True)
    productos = models.ManyToManyField(Product, related_name='promociones', blank=True)

    def __str__(self):
        return self.nombre

class PromocionText(models.Model):
    texto = models.CharField(max_length=255)


class Delivery (models.Model):
    limit = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=9.99)




class StoreSettings(models.Model):
    header_text = models.CharField(max_length=255)
    is_open = models.BooleanField(default=False)
    facebook_link = models.URLField(max_length=200, blank=True, null=True)
    linkedin_link = models.URLField(max_length=200, blank=True, null=True)
    instagram_link = models.URLField(max_length=200, blank=True, null=True)
    twitter_link = models.URLField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.header_text

    @classmethod
    def get_instance(cls):
        instance, created = cls.objects.get_or_create(id=1)
        return instance
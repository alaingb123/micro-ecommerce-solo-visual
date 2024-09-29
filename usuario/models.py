from django.contrib.auth.models import AbstractUser, Group, Permission, User
from django.db import models
from django.db.models.signals import post_migrate
from django.apps import apps

# Create your models here.
def crear_municipios_iniciales(sender, **kwargs):
    if kwargs['app_config'].name == 'usuario':
        roles_iniciales = [
            "admin",
            "Proveedor",
            "cliente",
        ]
        for nombre in roles_iniciales:
            Rol.objects.get_or_create(nombre=nombre)
class Rol(models.Model):
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usuario')
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='usuarios', null=True)

    def __str__(self):
        return self.user.username



post_migrate.connect(crear_municipios_iniciales, sender=apps.get_app_config('usuario'))
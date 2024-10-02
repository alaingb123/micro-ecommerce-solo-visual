# urls.py
from django.urls import path
from . import views


app_name = 'ventas'
urlpatterns = [
    path('registrar-ventas/', views.registrar_ventas, name='registrar_ventas'),
    path('ventas_exitosas/', views.ventas_exitosas , name='ventas_exitosas'),
    path('listar_ventas/', views.listar_ventas , name='listar_ventas'),


    # Otras rutas
]
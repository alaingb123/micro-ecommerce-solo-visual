from django.urls import path

from . import views

app_name = 'carro'
urlpatterns = [
    path('agregar/<int:product_id>/', views.agregar_producto, name='agregar'),
    path('agregar_cantidad/<int:product_id>/<int:quantity>/', views.agregar_producto_cantidad, name='agregar_cantidad'),
    path('agregar_carro/<int:product_id>/', views.agregar_producto_desde_carro, name='agregar_carro'),
    path('eliminar/<int:product_id>/', views.eliminar_producto, name='eliminar'),
    path('restar/<int:product_id>/', views.restar_producto, name='restar'),
    path('limpiar/', views.limpiar_carro, name='limpiar'),
    path('carro/', views.ver_carro, name='ver_carro'),

    path('contar/', views.contar_carro, name='contar_carro'),



]

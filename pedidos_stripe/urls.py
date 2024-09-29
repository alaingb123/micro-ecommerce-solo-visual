from django.urls import path

from . import views

app_name = 'pedidos_stripe'
urlpatterns = [

    # Compra con stripe
    path('start/', views.purchase_start_view, name='start'),
    path('buy_cart/<int:destinatario_id>', views.buy_cart_stripe, name='buy_cart'),
    path('purchases_stripe/', views.pedidos_stripe, name='purchases_stripe'),
    path('ver_solicitud_stripe/<int:purchase_id>', views.purchase_detail, name='ver_solicitud_stripe'),
    path('success_cart/', views.purchase_success_cart_view, name='success_cart'),
    path('success/', views.purchase_success_view, name='success'),
    path('stopped/', views.purchase_stopped_view, name='stopped'),


    path('ventas/', views.ventas, name='ventas'),
    path('ver_venta/<int:venta_id>/', views.ver_venta, name='ver_venta'),

    #estdo de pedido
    path('aceptar/<int:purchase_id>/', views.aceptar_pedido, name='aceptar'),
    path('entregar/<int:purchase_id>/', views.entregar_pedido, name='entregar'),
    path('cancelar/<int:purchase_id>/', views.cancelar_pedido, name='cancelar'),




]

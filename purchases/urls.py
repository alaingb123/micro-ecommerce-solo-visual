from django.urls import path

from . import views

app_name='purchases'
urlpatterns = [


    # COmpra con zelle
    path('create_solicitud/', views.create_solicitud, name='create_solicitud'),
    path('ver_solicitud/<int:id_solicitud>', views.view_solicitud_zelle, name='ver_solicitud'),
    path('list_solicitud/', views.solicitud_list, name='solicitud_list'),
    path('aceptar_solicitud/<int:id_solicitud>', views.aceptar_solicitud, name='aceptar_solicitud'),
    path('cancelar_solicitud/<int:id_solicitud>', views.cancelar_solicitud, name='cancelar_solicitud'),
    path('success_cart/', views.purchase_success_cart_view, name='success_cart'),
]

from django.urls import path

from . import views

app_name='purchases'
urlpatterns = [


    # COmpra con zelle
    path('create_solicitud_zelle/', views.create_solicitud_zelle, name='create_solicitud_zelle'),
    path('ver_solicitud/<int:id_solicitud>', views.view_solicitud_zelle, name='ver_solicitud'),
    path('list_solicitud/', views.solicitud_list, name='solicitud_list'),
    path('aceptar_solicitud/<int:id_solicitud>', views.aceptar_solicitud, name='aceptar_solicitud'),
    path('cancelar_solicitud/<int:id_solicitud>', views.cancelar_solicitud, name='cancelar_solicitud'),
]

from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from . import views

app_name='extra'
urlpatterns = [

    path('crear_destinatario/', views.crear_destinatario , name='crear_destinatario'),
    path('list_destinatario/', views.lista_destinatarios , name='list_destinatario'),
    path('editar_destinatario/<int:destinatario_id>', views.editar_destinatario , name='editar_destinatario'),
    path('eliminar_destinatario/<int:destinatario_id>', views.eliminar_destinatario , name='eliminar_destinatario'),


]
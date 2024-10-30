from django.contrib import admin

# Register your models here.

from .models import Solicitud, SolicitudItem


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'email', 'file', 'phone', 'payment_verification_code', 'amount', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user', 'email', 'phone')
        }),
        ('Información de la Solicitud', {
            'fields': ('products', 'file', 'payment_verification_code', 'amount', 'status')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(SolicitudItem)
class SolicitudItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitud', 'product', 'quantity', 'total_price')
    list_display_links = ('id', 'solicitud', 'product')
    readonly_fields = ('total_price',)

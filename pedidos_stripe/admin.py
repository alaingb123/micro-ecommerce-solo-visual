from django.contrib import admin

# Register your models here.

from .models import Purchase, SolicitudStripeItem


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'stripe_checkout_session_id', 'completed', 'stripe_price', 'timestamp', 'entrega')
    list_filter = ('completed', 'timestamp', 'entrega')
    search_fields = ('user__username', 'product__name', 'stripe_checkout_session_id')
    readonly_fields = ('user', 'stripe_checkout_session_id', 'completed', 'stripe_price', 'timestamp', 'entrega', 'product','nombre',
                       'apellidos','telefono','carnet_de_identidad','correo_electronico','direccion',
                       'municipio','instrucciones_entrega'
                                                                                        )


@admin.register(SolicitudStripeItem)
class VentaStripeItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'solicitud', 'total_price')
    list_filter = ('product', 'solicitud__completed', 'solicitud__entrega')
    search_fields = ('product__name',)
    readonly_fields = ('id', 'product', 'quantity', 'solicitud', 'total_price','product_price_snapshot','product_name_snapshot')




from django.contrib import admin

# Register your models here.

from .models import Product, ProductImage, ProductOffer, \
    Rating_product, Rating, Likes,Category


from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in Product._meta.fields if f.name != 'categories']  # Todos los campos son de solo lectura, excepto 'categories'
    list_display = ['name', 'user', 'price', 'active', 'handle', 'timestamp']  # Campos a mostrar en la lista
    search_fields = ['name', 'user__username', 'handle']  # Campos por los que se puede buscar
    list_filter = ['active']  # Campos por los que se puede filtrar

    def has_change_permission(self, request, obj=None):
        return True  # Permitir el cambio del objeto si es necesario

    def has_delete_permission(self, request, obj=None):
        return False  # Evita que se pueda eliminar el modelo


admin.site.register(Product, ProductAdmin)





class Rating_productAdmin(admin.ModelAdmin):
    list_display = ('product', 'average_rating')

    def has_add_permission(self, request):
        return False  # Evita que se pueda añadir un nuevo rating

    def has_change_permission(self, request, obj=None):
        return False  # Evita que se pueda cambiar un rating existente

    def has_delete_permission(self, request, obj=None):
        return False  # Evita que se pueda eliminar un rating

admin.site.register(Rating_product, Rating_productAdmin)




class ProductOfferAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_premium', 'is_active')
    search_fields = ('product__name',)  # Permite buscar por el nombre del producto
    fields = ('product', 'is_premium')  # Solo permitimos cambiar el producto y el campo is_premium
    readonly_fields = ('precio_nuevo', 'precio_viejo', 'start_date', 'end_date', 'is_active')  # Hacemos que los demás campos sean de solo lectura
    actions = ['execute_update_offers']  # Registramos la acción personalizada

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def execute_update_offers(self, request, queryset):
        for offer in queryset:
            offer.is_offer_active()  # Asegúrate de que esta función esté definida en tu modelo
        self.message_user(request, "Ofertas actualizadas exitosamente.")

    execute_update_offers.short_description = "Actualizar ofertas"

admin.site.register(ProductOffer, ProductOfferAdmin)

@admin.register(Likes)
class LikesAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'timestamp']










from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Personalizar el título del admin
admin.site.site_header = _("Administración de E-commerce")
admin.site.site_title = _("E-commerce")
admin.site.index_title = _("Bienvenido al panel de administración de E-Commerce")


from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from .models import Category
class MyAdmin(TreeAdmin):
    form = movenodeform_factory(Category)

admin.site.register(Category, MyAdmin)
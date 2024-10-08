from django.contrib import admin

from extra.models import Municipio, Destinatario, Promocion, StoreSettings
from products.models import Product

# Register your models here.
admin.site.register(Municipio)
admin.site.register(StoreSettings)


@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):


    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "productos":
            kwargs["queryset"] = Product.objects.all().order_by('name')
            kwargs['widget'] = admin.widgets.FilteredSelectMultiple(verbose_name='Productos', is_stacked=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

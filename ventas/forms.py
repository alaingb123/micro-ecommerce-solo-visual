
from django import forms
from django.db.models import Count

from products.models import Product

class VentaFilterForm(forms.Form):
    producto = forms.ModelChoiceField(queryset=Product.objects.none(), required=False)  # Inicializa como vacío
    fecha_inicio = forms.DateField(required=False, widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    fecha_fin = forms.DateField(required=False, widget=forms.widgets.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtener el usuario desde kwargs
        super(VentaFilterForm, self).__init__(*args, **kwargs)
        if user is not None:
            # Filtrar productos activos que pertenecen al usuario y que tienen al menos una venta
            self.fields['producto'].queryset = Product.objects.filter(
                user=user,
                active=True
            ).annotate(num_ventas=Count('venta')).filter(num_ventas__gt=0)


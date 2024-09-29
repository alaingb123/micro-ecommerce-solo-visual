from django import forms
from django.forms import modelformset_factory, inlineformset_factory, NumberInput
from .models import Product, ProductImage, ProductOffer, ClasificacionPadre, ClasificacionHija





class ProductForm(forms.ModelForm):
    clasificaciones_padre = forms.ModelChoiceField(
        queryset=ClasificacionPadre.objects.all(),
        empty_label="Seleccione una clasificación padre",
        required=False
    )
    class Meta:
        model = Product
        fields = ['name', 'image','clasificaciones_padre','handle', 'price', 'supply', 'description']





class ProductUpdateForm(forms.ModelForm):
    clasificaciones_padre = forms.ModelChoiceField(
        queryset=ClasificacionPadre.objects.all(),
        empty_label="Seleccione una clasificación",
        required=False
    )

    class Meta:
        model = Product
        fields = [
            "image", 'name', 'keywords', 'clasificaciones_padre',
             'handle', 'price', 'supply',
            'description', 'short_description', 'active'
        ]

    def __init__(self, *args, **kwargs):
        super(ProductUpdateForm, self).__init__(*args, **kwargs)
        self.fields['clasificaciones_padre'].queryset = ClasificacionPadre.objects.all()  # O fil
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})







class ProductAttachmentForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ["file", 'name', 'is_free', 'active']



ProductAttachmentModelFormSet = modelformset_factory(
    ProductImage,
    form=ProductAttachmentForm,
    fields = ['file', 'name','is_free', 'active'],
    extra=0,
    can_delete=True
)

ProductAttachmentInlineFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form = ProductAttachmentForm,
    formset = ProductAttachmentModelFormSet,
    fields = ['file', 'name','is_free', 'active'],
    extra=0,
    can_delete=True
)



class ProductOfferForm(forms.ModelForm):
    precio_nuevo = forms.DecimalField(decimal_places=2, localize=True)

    class Meta:
        model = ProductOffer
        fields = ['precio_nuevo', 'start_date', 'end_date']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("La fecha de inicio debe ser anterior a la fecha de finalización")

        return cleaned_data
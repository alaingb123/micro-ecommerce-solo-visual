from django import forms

from purchases.models import SolicitudZelle


class SolicitudZelleForm(forms.ModelForm):
    class Meta:
        model = SolicitudZelle
        fields = ['email', 'file', 'phone', 'payment_verification_code']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance

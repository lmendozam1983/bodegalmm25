from django import forms
from .models import Notificacion, Producto


class SolicitudProductoForm(forms.ModelForm):
    class Meta:
        model = Notificacion
        fields = ['producto', 'mensaje']  # O lo que necesites de los campos del modelo

    producto = forms.ModelChoiceField(queryset=Producto.objects.all(), widget=forms.Select(attrs={'class': 'form-select mb-3'}))
    mensaje = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control mb-3',
        'placeholder': 'Motivo de la solicitud',
        'rows': 4,
        'style': 'resize: none;'
    }))

    
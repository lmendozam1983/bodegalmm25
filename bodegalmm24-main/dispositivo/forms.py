from django import forms  
from .models import DeviceModel
from .models import PrestamoModel
from .models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Bodega



class DeviceForm(forms.ModelForm): 
    # specify the name of model to use 
    class Meta: 
        model = DeviceModel 
        fields = ['nombre', 'precio', 'bodega', 'descripcion', 'stock', 'serial', 'estado',]
        bodega = forms.ModelChoiceField(
        queryset=Bodega.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})  # Aplica la clase 'form-control'
    )
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado'].widget.attrs['readonly'] = True
                
class AdminDeviceForm(forms.ModelForm):
    class Meta:
        model = DeviceModel
        fields = '__all__'
        widgets = {
            'numero_serie': forms.TextInput(attrs={'readonly': 'readonly'}),
        }        

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True)
    foto_perfil = forms.ImageField(required=False)  # Campo para la imagen de perfil

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "foto_perfil")

    def save(self, commit=True):
        user = super(RegistroUsuarioForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Guardar la imagen en el perfil del usuario
            user.profile.foto_perfil = self.cleaned_data['foto_perfil']
            user.profile.save()
        return user

class PrestamoForm(forms.ModelForm):
    class Meta:
        model = PrestamoModel
        fields = ['usuario', 'dispositivo']
        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-control'}),
            'dispositivo': forms.Select(attrs={'class': 'form-control'}),
        }
        
class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['foto_perfil']
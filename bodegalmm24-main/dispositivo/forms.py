from django import forms  
from .models import DeviceModel
from .models import PrestamoModel
from .models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Bodega
from django.forms.widgets import ClearableFileInput
from django.utils.safestring import mark_safe

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        
        def clean_email(self):
            email = self.cleaned_data.get("email")
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Este correo electrónico ya está en uso.")
            return email

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


    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(RegistroUsuarioForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Guardar la imagen en el perfil del usuario
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
        
        
class CustomClearableFileInput(ClearableFileInput):
    """ Personaliza el widget para eliminar el texto 'Currently: ...' """
    initial_text = "Actual imagen ---------------->"  # Esto oculta 'Currently: ...'
    input_text = "Seleccionar imagen"
    clear_checkbox_label = "Eliminar imagen"  # Cambia el texto del checkbox
    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs["class"] = attrs.get("class", "") + " custom-file-input"  # Agrega estilos

        html = f"""
        <div class="mb-3">
            <input type="file" class="form-control" name="{name}" {self.build_attrs(attrs)}>
        </div>
        """
        return mark_safe(html)  # Devuelve HTML seguro

class EditarPerfilForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")
    first_name = forms.CharField(required=True, label="Nombre")
    last_name = forms.CharField(required=True, label="Apellido")
    foto_perfil = forms.ImageField(
        required=False,  
        widget=CustomClearableFileInput()
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control rounded-3 shadow-sm", "rows": 1}),
        required=False
    )
    DEPARTAMENTOS = [
        ('dirección', 'Dirección'),
        ('docente', 'Docente'),
        ('alumno', 'Alumno'),
        ('auxiliar', 'Auxiliar'),
        ('administrativo', 'Administrativo'),
        ('pie', 'Pie'),
        ('convivencia escolar', 'Convivencia escolar'),
    ]

    departamento = forms.ChoiceField(
        choices=DEPARTAMENTOS, 
        widget=forms.Select(attrs={'class': 'form-control'}), 
        required=True
    )

    class Meta:
        model = Profile
        fields = ['foto_perfil', 'first_name', 'last_name', 'email', 'telefono', 'direccion', 'bio', 'departamento']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(EditarPerfilForm, self).__init__(*args, **kwargs)
        # Personaliza la apariencia de los campos si usas Bootstrap
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
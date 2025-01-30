from django.contrib import admin
from .models import DeviceModel, ImagenUsuario, Bodega, User
from .forms import CustomUserCreationForm
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class CustomUserCreationForm(UserAdmin):
    add_form = CustomUserCreationForm
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "first_name", "last_name", "password1", "password2"),
        }),
    )
    
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    
admin.site.unregister(User)
admin.site.register(User, CustomUserCreationForm)

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'descripcion', 'stock')  # Muestra el campo dinámico en la lista
    search_fields = ('nombre', 'precio')  # Agrega opciones de búsqueda
    list_filter = ('stock',)  # Permite filtrar por valoración

@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')  # Personaliza las columnas visibles
    search_fields = ('nombre',)  # Agrega una barra de búsqueda para nombres

        
@admin.register(ImagenUsuario)
class ImagenUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'descripcion', 'fecha_subida', 'imagen')  # Incluye la imagen en la vista
    list_filter = ('fecha_subida',)
    search_fields = ('usuario__username', 'descripcion')
    readonly_fields = ('fecha_subida',)  # Campo de solo lectura
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('usuario', 'descripcion')
        }),
        ('Imagen', {
            'fields': ('imagen', 'fecha_subida')
        }),
    )


admin.site.register(DeviceModel)
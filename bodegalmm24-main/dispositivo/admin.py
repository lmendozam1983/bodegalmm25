from django.contrib import admin
from .models import DeviceModel, ImagenUsuario, Bodega, User #Profile
from .forms import CustomUserCreationForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Register your models here.

#class ProfileInline(admin.StackedInline):
    #model = Profile
    #can_delete = False
    #verbose_name_plural = "Perfil"

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm  # Usa el nuevo formulario en la creación de usuarios
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'rut', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    #inlines = [ProfileInline]
    
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

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
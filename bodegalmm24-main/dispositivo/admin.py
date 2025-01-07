from django.contrib import admin
from .models import DeviceModel, ImagenUsuario

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'descripcion', 'stock')  # Muestra el campo dinámico en la lista
    search_fields = ('nombre', 'precio')  # Agrega opciones de búsqueda
    list_filter = ('stock',)  # Permite filtrar por valoración
        
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
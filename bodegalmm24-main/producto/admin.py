from django.contrib import admin
from .models import Producto, Bodega

# Register your models here.
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad', 'precio_unitario', 'fecha_ingreso')
    search_fields = ('nombre',)
    list_filter = ('fecha_ingreso',)
    
@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')  # Personaliza las columnas visibles
    search_fields = ('nombre',)  # Agrega una barra de búsqueda para nombres
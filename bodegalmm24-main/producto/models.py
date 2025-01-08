from django.db import models
from django.contrib.auth.models import User



# Create your models here.
class Bodega(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del producto")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name='producto', null=True)
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad en stock")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    fecha_ingreso = models.DateField(auto_now_add=True, verbose_name="Fecha de ingreso")
    class Meta:
        permissions = [
            ("visualizar_listado", "Puede visualizar el listado de productos"),
        ]

    def __str__(self):
        return self.nombre

    
class Notificacion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mensaje = models.TextField()  # Campo para el mensaje
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    aprobada = models.BooleanField(default=False)
    # Opcional: Agregar un campo de estado
    ESTADOS = (
        ('Pendiente', 'Pendiente'),
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
    )
    estado = models.CharField(max_length=10, choices=ESTADOS, default='Pendiente')
        
    def __str__(self):
        return f"Notificación de {self.usuario.username} para {self.producto.nombre}"

    class Meta:
        ordering = ['-fecha_creacion']
        
class Prestamo(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="prestamos_realizados")  # Usuario que realiza el préstamo
    usuario_destino = models.ForeignKey(User, on_delete=models.CASCADE, related_name="prestamos_recibidos", null=True, blank=True) # Usuario que recibe el préstamo
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name='prestamos',  null=True)
    cantidad = models.PositiveIntegerField()
    fecha_prestamo = models.DateTimeField(auto_now_add=True)
    notificacion = models.ForeignKey(Notificacion, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.usuario} - {self.producto.nombre} - {self.cantidad}"



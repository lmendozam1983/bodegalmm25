from django.db import models
from django.contrib.auth.models import User
import uuid



# Create your models here.
class Bodega(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    
    DESCRIPCION_CHOICES = [
        ('Pañol', 'Pañol'),
        ('Bodega Audio', 'Bodega Audio'),
    ]

    tipo_bodega = models.CharField(
        max_length=50,
        choices=DESCRIPCION_CHOICES,
        verbose_name="Tipo de bodega",
        blank=True,
    )

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del producto")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name='producto', null=True)
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad en stock")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    fecha_ingreso = models.DateField(auto_now_add=True, verbose_name="Fecha de ingreso")
    numero_serie = models.CharField(max_length=20, unique=True, editable=False, default="")
    imagen = models.ImageField(upload_to='productos/', default='productos/default-placeholder.png')

    
    DESCRIPCION_CHOICES = [
        ('Aseo', 'Aseo'),
        ('Oficina', 'Oficina'),
        ('Ferretería', 'Ferretería'),
        ('Lab_Electronica', 'Lab_Electronica'),
        ('Lab_Telecomunicaciones', 'Lab_Telecomunicaciones'),
        ('Herramientas', 'Herramientas'),
        ('Toner_Tintas', 'Toner_Tintas'),
    ]

    tipo_descripcion = models.CharField(
        max_length=50,
        choices=DESCRIPCION_CHOICES,
        verbose_name="Tipo de descripción",
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.numero_serie:  # Generar solo si no existe
            self.numero_serie = self.generar_numero_serie()
        super().save(*args, **kwargs)

    def generar_numero_serie(self):
        return f"PROD-{uuid.uuid4().hex[:12].upper()}"  # Ejemplo: PROD-A1B2C3D4E5F6
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
    cantidad = models.PositiveIntegerField(null=False, blank=False) 
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



from django.db import models
from django.contrib.auth.models import User
import uuid
from django.core.exceptions import ValidationError
import re

# Create your models here.
class Bodega(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nombre

class DeviceModel(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name='producto', null=True)
    descripcion = models.TextField()
    stock = models.PositiveIntegerField(default=1)
    serial = models.CharField(max_length=20, unique=True, editable=False, default="")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        verbose_name = "Dispositivo"
        verbose_name_plural = "Dispositivos"
        permissions = (
                ("development", "Puede desarrollar"),
                ("scrum_master", "Es Scrum Master"),
                ("visualizar_listado", "visualizar listado"),
                ("superuser", "superuser" )
        )
    
    ESTADO_CHOICES = [
        ('Disponible', 'Disponible'),
        ('No Disponible', 'No Disponible'),
        ('Prestado', 'Prestado'),
        ('Mantenimiento', 'Mantenimiento'),
    ]
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='Disponible')
    
    def marcar_como_prestado(self):
        if not hasattr(self, 'estado'):
            raise AttributeError("El campo 'estado' no existe en este objeto.")
        if self.estado != 'Disponible':
            raise ValueError("El dispositivo no está disponible.")
        self.estado = 'Prestado'
        self.save()
        
    def save(self, *args, **kwargs):
        if not self.serial:  # Generar solo si no existe
            self.serial = self.generar_numero_serie()
        super().save(*args, **kwargs)

    def generar_numero_serie(self):
        return f"DISP-{uuid.uuid4().hex[:12].upper()}"  # Ejemplo: DISP-A1B2C3D4E5F6
    class Meta:
        permissions = [
            ("visualizar_listado", "Puede visualizar el listado de productos"),
        ]
        
    def __str__(self):
        return f"{self.nombre} ({self.serial})"

class PrestamoModel(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    dispositivo = models.ForeignKey(DeviceModel, on_delete=models.CASCADE)
    fecha_prestamo = models.DateTimeField(auto_now_add=True)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=50, choices=[('Pendiente', 'Pendiente'), ('Devuelto', 'Devuelto')])

    def devolver(self):
        """Método para devolver el dispositivo y actualizar su estado"""
        if self.estado == 'Pendiente':
            self.estado = 'Devuelto'
            self.save()
            self.dispositivo.estado = 'Disponible'
            self.dispositivo.save()

    def __str__(self):
        return f"Préstamo de {self.dispositivo.nombre} a {self.usuario.username}"


def validar_rut(value):
    """ Valida que el RUT tenga el formato correcto. """
    if not re.match(r'^\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]$', value):
        raise ValidationError('El RUT ingresado no es válido. Debe tener el formato XXXXXXXX-X.')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    departamento = models.CharField(max_length=255, blank=True, null=True)
    rut = models.CharField(max_length=12, unique=True, validators=[validar_rut], null=True, blank=True)# Nuevo campo
    
    def __str__(self):
        return self.user.username
    
class ImagenUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='fotos_perfil/')
    descripcion = models.TextField(blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.descripcion or 'Sin descripción'}"
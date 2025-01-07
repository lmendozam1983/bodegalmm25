from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class DeviceModel(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    stock = models.PositiveIntegerField()
    serial = models.CharField(max_length=255, unique=True)
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
        if not self.serial:
            self.serial = self.generar_numero_serie()
        super().save(*args, **kwargs)

    def generar_numero_serie(self):
        # Generar un número secuencial a partir de la cantidad de dispositivos en la base de datos
        ultimo_dispositivo = DeviceModel.objects.last()  # Último dispositivo guardado
        if ultimo_dispositivo:
            # Si hay dispositivos, el nuevo número de serie será el siguiente
            siguiente_numero = int(ultimo_dispositivo.serial.split("-")[-1]) + 1
        else:
            # Si no hay dispositivos, comienza desde 1
            siguiente_numero = 1
        return f"SN-{siguiente_numero}"
        
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

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)

    def __str__(self):
        return self.user.username
    
class ImagenUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='fotos_perfil/')
    descripcion = models.TextField(blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.descripcion or 'Sin descripción'}"
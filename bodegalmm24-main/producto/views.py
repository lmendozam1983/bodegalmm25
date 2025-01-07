from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto, Prestamo
from django.contrib import messages 
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Producto, Prestamo
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Producto, Prestamo
from .models import Notificacion
from .forms import SolicitudProductoForm
from django.core.paginator import Paginator
from django.http import HttpResponse
from datetime import timedelta
from .models import Producto, Bodega


# Create your views here.
def lista_productos(request):
    productos = Producto.objects.select_related('bodega').all()
    return render(request, 'lista_productos.html', {'productos': productos})

@login_required
@permission_required('producto.crear_producto', raise_exception=True)
def crear_producto(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        cantidad = request.POST['cantidad']
        precio_unitario = request.POST['precio_unitario']
        descripcion = request.POST['descripcion']
        bodega_id = request.POST.get('bodega')  # Obtener la bodega seleccionada desde el formulario

        # Obtener la instancia de la bodega seleccionada
        bodega = Bodega.objects.get(id=bodega_id)

        # Crear el producto asociado con la bodega
        Producto.objects.create(
            nombre=nombre,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            descripcion=descripcion,
            bodega=bodega,  # Asociar el producto a la bodega seleccionada
        )
        return redirect('lista_productos')

    # Pasar todas las bodegas al contexto para el formulario
    bodegas = Bodega.objects.all()
    return render(request, 'crear_productos.html', {'bodegas': bodegas})


@login_required
def prestar_producto(request, producto_id):
    # Obtener el producto o lanzar error 404 si no se encuentra
    producto = get_object_or_404(Producto, id=producto_id)

    # Obtener todos los usuarios disponibles para seleccionar (puedes filtrarlos si es necesario)
    usuarios = User.objects.all()

    if request.method == 'POST':
        # Intentamos obtener la cantidad desde el formulario y convertirla a entero
        try:
            cantidad = int(request.POST['cantidad'])
            usuario_id = int(request.POST['usuario'])
        except (ValueError, KeyError):
            messages.error(request, "La cantidad ingresada o el usuario seleccionado no son válidos.")
            return redirect('prestar_producto', producto_id=producto.id)

        # Verificar que la cantidad no exceda el stock disponible
        if cantidad > producto.cantidad:
            messages.error(request, "No hay suficiente stock disponible.")
            return redirect('prestar_producto', producto_id=producto.id)

        # Verificar que el usuario seleccionado existe
        try:
            usuario_destino = User.objects.get(id=usuario_id)
        except User.DoesNotExist:
            messages.error(request, "El usuario seleccionado no existe.")
            return redirect('prestar_producto', producto_id=producto.id)

        # Crear el préstamo
        try:
            Prestamo.objects.create(
                usuario=request.user,  # Usuario que hace el préstamo
                producto=producto,
                cantidad=cantidad,
                usuario_destino=usuario_destino  # Usuario que recibe el préstamo
            )
        except Exception as e:
            messages.error(request, f"Hubo un error al procesar el préstamo: {str(e)}")
            return redirect('prestar_producto', producto_id=producto.id)

        # Actualizar el stock del producto
        producto.cantidad -= cantidad
        producto.save()

        # Mensaje de éxito
        messages.success(request, f"Se ha prestado {cantidad} unidad(es) de {producto.nombre} a {usuario_destino.username}.")
        return redirect('detalle_producto', producto_id=producto.id)

    # Renderizamos el formulario si la solicitud es GET
    return render(request, 'prestar_productos.html', {'producto': producto, 'usuarios': usuarios})
@login_required
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'detalle_producto.html', {'producto': producto})

@login_required
def prestamos_producto(request, producto_id):
    # Obtener el producto específico
    producto = get_object_or_404(Producto, id=producto_id)

    # Obtener los préstamos del producto específico
    prestamos = Prestamo.objects.filter(producto=producto)

    # Obtener las notificaciones necesarias, puedes filtrarlas si es necesario
    notificaciones = Notificacion.objects.all()

    # Pasar los préstamos, producto y notificaciones a la plantilla
    context = {
        'producto': producto,
        'prestamos': prestamos,
        'notificaciones': notificaciones,
    }

    # Renderizar la plantilla con el contexto
    return render(request, 'prestamos_producto.html', context)

@login_required
def agregar_stock(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        try:
            cantidad_a_agregar = int(request.POST['cantidad'])
            if cantidad_a_agregar <= 0:
                messages.error(request, "La cantidad debe ser un número positivo.")
                return redirect('agregar_stock', producto_id=producto.id)

            # Agregar la cantidad al stock actual
            producto.cantidad += cantidad_a_agregar
            producto.save()

            messages.success(request, f"Se han agregado {cantidad_a_agregar} unidades de {producto.nombre}.")
            return redirect('detalle_producto', producto_id=producto.id)

        except ValueError:
            messages.error(request, "La cantidad ingresada no es válida.")
            return redirect('agregar_stock', producto_id=producto.id)

    return render(request, 'agregar_stock.html', {'producto': producto})

@login_required
def panel_solicitudes(request):
    
    # Obtén todas las notificaciones
    notificaciones = Notificacion.objects.all()

    return render(request, 'panel_solicitudes.html', {'notificaciones': notificaciones})

@login_required
def marcar_como_leido(request, notificacion_id):
    # Solo el admin puede realizar esta acción
    if not request.user.is_staff:
        return redirect('home')  # Redirige si no es admin

    notificacion = get_object_or_404(Notificacion, id=notificacion_id)
    notificacion.leida = True
    notificacion.save()

    # Redirigir al panel de solicitudes
    return redirect('panel_solicitudes')

@login_required
def solicitar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = SolicitudProductoForm(request.POST)
        if form.is_valid():
            # En vez de crear una instancia de SolicitudProducto, creamos una de Notificacion
            mensaje = form.cleaned_data['mensaje']
            
            # Crear la notificación, que también contiene la solicitud
            notificacion = Notificacion(
                usuario=request.user,
                producto=producto,
                mensaje=mensaje,  # El mensaje del formulario será usado para la solicitud
            )
            notificacion.save()

            messages.success(request, f"Has solicitado el producto {producto.nombre}. El administrador revisará tu solicitud.")
            return redirect('lista_productos')  # Redirige a la lista de productos
    else:
        form = SolicitudProductoForm()

    return render(request, 'solicitar_producto.html', {'form': form, 'producto': producto})



def aprobar_solicitud(request, notificacion_id):
    # Buscar la notificación por su ID
    notificacion = get_object_or_404(Notificacion, id=notificacion_id)

    # Verificar que el usuario sea un administrador
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para aprobar solicitudes.")
        return redirect('home')  # Redirige a una página predeterminada

    # Cambiar el estado de la solicitud a "aprobada"
    notificacion.estado = 'Aprobada'  # Asumiendo que 'estado' es un campo en el modelo Notificacion
    notificacion.save()

    # Enviar un mensaje de éxito
    messages.success(request, f"La solicitud para el producto {notificacion.producto.nombre} ha sido aprobada.")

    # Redirigir a la lista de solicitudes pendientes
    return redirect('listar_solicitudes')  # Redirige a la URL que corresponda

@login_required
def listar_solicitudes(request):
    solicitudes = Notificacion.objects.filter(estado='Pendiente')
    paginator = Paginator(solicitudes, 10)  # Muestra 10 solicitudes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'listar_solicitudes.html', {'page_obj': page_obj})

@login_required
def listar_notificaciones(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, 'notificaciones.html', {'notificaciones': notificaciones})

def generar_voucher(request, notificacion_id):
    # Obtén la notificación
    notificacion = get_object_or_404(Notificacion, id=notificacion_id)
    prestamo = Prestamo.objects.filter(usuario=notificacion.usuario)
    
    context = {
        'usuario': notificacion.usuario,
        'producto': notificacion.producto,
        'fecha_prestamo': notificacion.fecha_creacion,
        'fecha_devolucion': notificacion.fecha_creacion + timedelta(days=7),  # Ejemplo: 7 días después
        'prestamos': prestamo
    }
    return render(request, 'voucher.html', context)

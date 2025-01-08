# Django
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect#
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Permission
from django.contrib.auth import authenticate
from django.contrib import messages 
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test


# Local Proyecto Django
from .forms import DeviceForm
from .forms import DeviceForm, RegistroUsuarioForm 
from .forms import RegistroUsuarioForm
from .models import DeviceModel
from .models import PrestamoModel
from .forms import PrestamoForm
from .forms import EditarPerfilForm  
from .models import ImagenUsuario

# Create your views here.

def index(request):
    return render(request, 'index.html')

def listadoView(request):
    dispositivos = DeviceModel.objects.select_related('bodega').all().order_by('id')  # Obtén los datos
    paginator = Paginator(dispositivos, 10) # Configura el paginador para 10 registros por página
    page_number = request.GET.get('page', 1) # Obtén el número de página actual de la solicitud GET
    page_obj = paginator.get_page(page_number)  # Obtén la página correspondiente
    return render(request, 'listado.html', {'page_obj': page_obj})  # Solo pasamos 'page_obj'


@login_required
@permission_required('dispositivo.visualizar_listado', raise_exception=True)
def deviceform_view(request):
    context = {}

    # Cargar el formulario con los datos del POST si está disponible
    form = DeviceForm(request.POST or None, request.FILES or None)

    # Estilos personalizados
    form.fields['nombre'].widget.attrs.update({'class': 'form-control custom-input'})
    form.fields['precio'].widget.attrs.update({'class': 'form-control custom-input'})
    form.fields['descripcion'].widget.attrs.update({'class': 'form-control custom-input'})
    form.fields['stock'].widget.attrs.update({'class': 'form-control custom-input'})

    # Verificar si el formulario es válido
    if form.is_valid():
        form.save()
        messages.success(request, "Dispositivo registrado exitosamente.")
        return redirect('/')  # Redirige a la página principal o la vista deseada

    # Pasar el formulario al contexto para renderizarlo en la plantilla
    context['form'] = form
    return render(request, 'ingresar.html', context)

def editar(request, dispositivo_id):
    dispositivo = get_object_or_404(DeviceModel, pk=dispositivo_id)
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=dispositivo)
        if form.is_valid():
            form.save()
            return redirect('listado')  # Cambia 'listado' por el nombre de tu vista de listado
    else:
        form = DeviceForm(instance=dispositivo)
    return render(request, 'editar.html', {'form': form})

def eliminar(request, dispositivo_id):
    dispositivo = get_object_or_404(DeviceModel, pk=dispositivo_id)

    if request.method == "POST":
        dispositivo.delete()
        return redirect('listado')  # Redirige al listado de dispositivos después de eliminar

    return render(request, 'confirmar_eliminacion.html', {'dispositivo': dispositivo})


def loginView(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Iniciaste sesión como: {username}.")
                next_url = '/index/'
                return HttpResponseRedirect('/')
            else:
                messages.error(request,"Invalido username o password.")
        else:
            messages.error(request,"Invalido username o password.")
    form = AuthenticationForm()
    return render(request, "registration/login.html", {"login_form": form})


def registroView(request): 
    if request.method == "POST": 
        form = RegistroUsuarioForm(request.POST) 
        if form.is_valid(): 
            content_type = ContentType.objects.get_for_model(DeviceModel) 
            visualizar_listado = Permission.objects.get(
                codename='visualizar_listado', 
                content_type=content_type
            ) 
            user = form.save() 
            user.user_permissions.add(visualizar_listado) 
            login(request, user)
            next_url = '/'
            messages.success(request, "Registrado satisfactoriamente.") 
            return HttpResponseRedirect('/')
        else:
            messages.error(request, "Registro inválido. Algunos datos son incorrectos.") 
    else:
        form = RegistroUsuarioForm()  
    
    return render(request, 'registration/registro.html', {'register_form': form})

def logoutView(request):
    logout(request)
    messages.info(request, "Se ha cerrado la sesión satisfactoriamente.")
    return HttpResponseRedirect('/') 

@permission_required('dispositivo.visualizar_listado', raise_exception=True)
def registrar_prestamo(request):
    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            prestamo = form.save(commit=False)
            dispositivo = prestamo.dispositivo  # Obtenemos el dispositivo asociado al préstamo

            # Verificamos si el objeto es una instancia válida de DeviceModel
            if isinstance(dispositivo, DeviceModel):
                try:
                    # Intentamos marcar el dispositivo como prestado
                    if dispositivo.estado == 'Disponible':
                        dispositivo.estado = 'Prestado'
                        dispositivo.save()  # Guardamos el cambio de estado en el dispositivo
                        prestamo.save()  # Guardamos el préstamo
                        messages.success(request, "El préstamo se registró exitosamente")
                        return redirect('listado_prestamos')
                    else:
                        form.add_error('dispositivo', 'El dispositivo no está disponible.')
                except ValueError as e:
                    form.add_error('dispositivo', str(e))
            else:
                form.add_error('dispositivo', "El objeto no es un dispositivo válido.")
        else:
            messages.error(request, "Hubo un error al registrar el préstamo. Verifique los datos.")
    else:
        form = PrestamoForm()

    return render(request, 'registrar_prestamo.html', {'form': form})

@permission_required('dispositivo.visualizar_listado', raise_exception=True)
def eliminar_prestamos(request, prestamo_id):
    # Obtener el préstamo a eliminar usando el prestamo_id
    prestamo = get_object_or_404(PrestamoModel, id=prestamo_id)
    
    # Verificar que el préstamo esté devuelto
    if prestamo.estado == 'Pendiente':
        messages.error(request, "El préstamo aún está pendiente de devolución.")
        return redirect('listado')  # Redirigir a donde corresponda

    # Actualizar el estado del dispositivo a 'Disponible'
    dispositivo = prestamo.dispositivo
    dispositivo.estado = 'Disponible'
    dispositivo.save()

    # Eliminar el préstamo
    prestamo.delete()

    # Mensaje de éxito
    messages.success(request, f"El préstamo de {dispositivo.nombre} ha sido eliminado y el dispositivo está disponible.")

    # Redirigir a la página de listado de dispositivos
    return redirect('listado')  # Ajusta esto a la vista de listado

    

def listado_prestamos(request):
    prestamos = PrestamoModel.objects.all()
    return render(request, 'listado_prestamos.html', {'prestamos': prestamos})

def listar_usuarios(request):
    usuarios = User.objects.all()  # Obtener todos los usuarios
    return render(request, 'listar_usuarios.html', {'usuarios': usuarios})

def generar_codigo_barras(numero_serie):
    codigo = Code128(numero_serie, writer=ImageWriter())
    filename = f"codigos/{numero_serie}"
    codigo.save(filename)
    return filename

@login_required
def perfilView(request):
    profile = request.user.profile  # Recupera el perfil del usuario autenticado
    return render(request, 'registration/perfil.html', {'profile': profile})

@login_required
def editarPerfilView(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('perfil')
    else:
        form = EditarPerfilForm(instance=profile)

    return render(request, 'registration/editar_perfil.html', {'form': form})

@permission_required('dispositivo.visualizar_listado', raise_exception=True)
def ver_imagenes_subidas(request):
    imagenes = ImagenUsuario.objects.select_related('usuario').order_by('-fecha_subida')
    print(imagenes)
    return render(request, 'ver_imagenes.html', {'imagenes': imagenes})

def ver_imagenes(request):
    imagenes = ImagenUsuario.objects.select_related('usuario').order_by('-fecha_subida')
    context = {
        'imagenes': imagenes
    }
    return render(request, 'ver_imagenes.html', context)
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
import pandas as pd

# Local Proyecto Django
from .forms import DeviceForm
from .forms import DeviceForm, RegistroUsuarioForm 
from .forms import RegistroUsuarioForm
from .models import DeviceModel
from .models import PrestamoModel
from .forms import PrestamoForm
from .forms import EditarPerfilForm  
from .models import ImagenUsuario
from producto.models import Prestamo


# Create your views here.

def index(request):
    return render(request, 'index.html')

def listadoView(request):
    nombre = request.GET.get('nombre', '')
    estado = request.GET.get('estado', '')
    
    dispositivos = DeviceModel.objects.select_related('bodega').all().order_by('id')  # Obtén los datos
    
    if nombre:
        dispositivos = dispositivos.filter(nombre__icontains=nombre)  # Filtrar por nombre, caso insensible
    if estado:
        dispositivos = dispositivos.filter(estado=estado)  # Filtrar por tipo de descripción
        
    
    
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
        return redirect('listado')  # Redirige a la página principal o la vista deseada

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
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Solo mostrar el mensaje después de un login exitoso
                messages.info(request, f"Iniciaste sesión como: {username}.")
                # Redirigir a otra página para evitar recarga con mensaje
                return redirect('/')  # Asegúrate de tener la URL 'home' definida
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
        else:
            messages.error(request, "Por favor, completa el formulario correctamente.")

    else:
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
    prestamos = PrestamoModel.objects.order_by('id')  # Obtén los datos
    paginator = Paginator(prestamos, 10)  # Configura el paginador para 10 registros por página
    page_number = request.GET.get('page', 1)  # Obtén el número de página actual de la solicitud GET
    page_obj = paginator.get_page(page_number)  # Obtén la página correspondiente
    return render(request, 'listado_prestamos.html', {'page_obj': page_obj})
    

def listar_usuarios(request):
    usuarios = User.objects.all()  # Obtener todos los usuarios
    paginator = Paginator(usuarios, 10)  # Configura el paginador para 10 registros por página
    page_number = request.GET.get('page', 1)  # Obtén el número de página actual de la solicitud GET
    page_obj = paginator.get_page(page_number)  # Obtén la página correspondiente
    # Renderiza la plantilla con los préstamos en el contexto
    return render(request, 'listar_usuarios.html', {'page_obj': page_obj})

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
    profile = request.user.profile  # Obtener el perfil del usuario
    user = request.user  # Obtener el usuario

    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)  # Guardar perfil sin hacer commit aún
            
            # Actualizar datos del usuario si están en el formulario
            user.email = form.cleaned_data.get('email', user.email)
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name = form.cleaned_data.get('last_name', user.last_name)
            
            user.save()  # Guardar cambios en el usuario
            profile.save()  # Guardar cambios en el perfil

            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('perfil')  # Redirigir a la vista del perfil
    else:
        form = EditarPerfilForm(instance=profile, initial={
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        })

    return render(request, 'registration/editar_perfil.html', {'form': form})

@permission_required('dispositivo.visualizar_listado', raise_exception=True)
def ver_imagenes_subidas(request):
    imagenes = ImagenUsuario.objects.select_related('usuario').order_by('-fecha_subida')
    print(imagenes)
    return render(request, 'ver_imagenes.html', {'imagenes': imagenes})


@login_required
def historial_usuario_productos(request):
    # Filtra los préstamos realizados por el usuario autenticado y optimiza las relaciones
    prestamos = Prestamo.objects.filter(usuario=request.user).select_related('producto', 'bodega', 'notificacion').order_by('-fecha_prestamo')
    paginator = Paginator(prestamos, 10)  # Configura el paginador para 10 registros por página
    page_number = request.GET.get('page', 1)  # Obtén el número de página actual de la solicitud GET
    page_obj = paginator.get_page(page_number)  # Obtén la página correspondiente
    # Renderiza la plantilla con los préstamos en el contexto
    return render(request, 'historial_usuario_productos.html', {'page_obj': page_obj})

@login_required
def historial_usuario_dispositivos(request):
    # Obtener todos los préstamos, ordenados por fecha de préstamo (de más reciente a más antiguo)
    prestamos = PrestamoModel.objects.all().order_by('-fecha_prestamo')
    return render(request, 'historial_usuario_dispositivos.html', {'prestamos': prestamos})


from django.contrib.auth.views import PasswordResetView

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_email.html'
    email_template_name = 'registration/password_reset_email.html'
    
@login_required
@permission_required('dispositivo.visualizar_listado', raise_exception=True)
def importar_usuarios_excel(request):
    if request.method == 'POST' and request.FILES.get('archivo_excel'):
        archivo = request.FILES['archivo_excel']

        try:
            df = pd.read_excel(archivo, engine='openpyxl')

            # Validar que el archivo tenga las columnas requeridas
            columnas_requeridas = {'username', 'email', 'first_name', 'last_name', 'password'}
            if not columnas_requeridas.issubset(df.columns):
                messages.error(request, "El archivo no tiene las columnas requeridas.")
                return redirect('importar_usuarios')

            # Procesar cada fila
            for _, fila in df.iterrows():
                if User.objects.filter(username=fila['username']).exists():
                    messages.warning(request, f"El usuario {fila['username']} ya existe. Se omitió.")
                    continue

                usuario = User(
                    username=fila['username'],
                    email=fila['email'],
                    first_name=fila['first_name'],
                    last_name=fila['last_name'],
                )
                usuario.set_password(fila['password'])  # Encriptar la contraseña
                usuario.save()

            messages.success(request, "Usuarios importados correctamente.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {e}")

    return render(request, 'importar_usuarios.html')

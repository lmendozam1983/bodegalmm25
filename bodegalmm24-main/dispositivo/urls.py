from django.urls import path 
from . import views 

urlpatterns = [ 
    path('', views.index, name='index'), 
    path('templates/registration/login/', views.loginView, name='login'),
    path('templates/registration/registro/', views.registroView, name='registro'),
    path('logout/', views.logoutView, name='logout'),
    path('listado/', views.listadoView, name='listado'),
    path('templates/registrar_prestamo/', views.registrar_prestamo, name='registrar_prestamo'),
    path('templates/listado_prestamos/', views.listado_prestamos, name='listado_prestamos'),
    path('templates/eliminar_prestamos/<int:prestamo_id>/', views.eliminar_prestamos, name='eliminar_prestamos'),
    path('templates/ingresar/', views.deviceform_view, name='ingresar'),
    path('editar/<int:dispositivo_id>/', views.editar, name='editar'),
    path('eliminar/<int:dispositivo_id>/', views.eliminar, name='eliminar'),
    path('templates/listar_usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('templates/registration/perfil/', views.perfilView, name='perfil'),
    path('templates/registration/editar_perfil/', views.editarPerfilView, name='editar_perfil'),
    path('templates/ver_imagenes/', views.ver_imagenes_subidas, name='ver_imagenes_subidas'),
]
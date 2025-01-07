from django.urls import path
from . import views

urlpatterns = [
    path('templates/lista_productos/', views.lista_productos, name='lista_productos'),
    path('templates/crear_productos/', views.crear_producto, name='crear_producto'),
    path('templates/prestar_productos/<int:producto_id>', views.prestar_producto, name='prestar_producto'),
    path('templates/detalle_producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('templates/<int:producto_id>/prestamos_producto/', views.prestamos_producto, name='prestamos_producto'),
    path('templates/<int:producto_id>/agregar_stock/', views.agregar_stock, name='agregar_stock'),
    path('templates/panel_solicitudes/', views.panel_solicitudes, name='panel_solicitudes'),
    path('admin/marcar_como_leido/<int:notificacion_id>/', views.marcar_como_leido, name='marcar_como_leido'),
    path('admin/aprobar_solicitud/<int:notificacion_id>/', views.aprobar_solicitud, name='aprobar_solicitud'),  # Nueva URL
    path('templates/<int:producto_id>/solicitar_producto/', views.solicitar_producto, name='solicitar_producto'),
    path('templates/listar_solicitudes/', views.listar_solicitudes, name='listar_solicitudes'),
    path('templates/notificaciones/', views.listar_notificaciones, name='listar_notificaciones'),
    path('templates/voucher/<int:notificacion_id>/', views.generar_voucher, name='generar_voucher'),
]




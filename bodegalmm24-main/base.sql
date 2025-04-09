INSERT INTO public."dispositivo_devicemodel" (id, nombre, precio, descripcion, stock, serial, fecha_creacion, fecha_modificacion, estado)
VALUES 
(87,'Notebook Hp 240 G8 I3',0,'SEP-144',11,'700000000087',NOW(),NOW(),'Disponible'),
(88,'Notebook Hp 240 G8 I3',0,'SEP-145',11,'700000000088',NOW(),NOW(),'Disponible'),
(89,'Notebook Hp 240 G8 I3',0,'SEP-146',11,'700000000089',NOW(),NOW(),'Disponible');


def eliminar_prestamos(request, id):
    prestamo = get_object_or_404(PrestamoModel, id=id)
    
    if request.method == 'POST':
        # Si es un POST, eliminamos el préstamo
        prestamo.delete()
        return redirect('listado_prestamos')  # Redirige a la lista de préstamos
            return render(request, 'eliminar_prestamos.html', {'prestamo': prestamo})
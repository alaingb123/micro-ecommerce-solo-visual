from django.contrib import messages
from django.shortcuts import render, redirect

from products.models import Product, Venta
from usuario.decorator import role_required
from ventas.forms import VentaFilterForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.



@role_required(['Proveedor'])
def registrar_ventas(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':  # Ignora el token CSRF
                try:
                    producto_id = int(key)  # Convierte el ID del producto a entero
                    producto = Product.objects.get(id=producto_id)  # Obtiene el producto

                    if value.isdigit() and int(value) > 0:  # Verifica que la cantidad sea válida
                        cantidad = int(value)  # Convierte a entero

                        if producto.supply >= cantidad:  # Verifica si hay suficiente stock
                            producto.supply -= cantidad  # Reduce el stock
                            producto.save()  # Guarda el producto
                            Venta.objects.create(producto=producto, cantidad=cantidad,precio=producto.price)  # Crea la venta
                        else:
                            messages.error(request, f"No hay suficiente stock para {producto.name}.")
                            return redirect('ventas:registrar_ventas')  # Redirige a la misma página si hay error
                except Product.DoesNotExist:
                    messages.error(request, "Producto no encontrado.")  # Manejo de errores si el producto no existe
                    return redirect('ventas:registrar_ventas')
                except ValueError:
                    messages.error(request, "Cantidad no válida.")  # Manejo de cantidad no válida
                    return redirect('ventas:registrar_ventas')

        return redirect('ventas:ventas_exitosas')  # Redirige a la página de éxito

    productos = Product.objects.filter(user=request.user, active=True)  # Asegúrate de usar 'proveedor' y 'activo'
    return render(request, 'ventas/registrar_ventas.html', {'productos': productos})


@role_required(['Proveedor'])
def ventas_exitosas(request):
    return render(request, 'ventas/ventas_exitosas.html')

@role_required(['Proveedor'])
def listar_ventas(request):
    # Obtener las ventas del usuario autenticado
    ventas = Venta.objects.filter(producto__user=request.user, producto__active=True).order_by('-fecha_venta')

    # Filtrado por producto y fecha
    form = VentaFilterForm(request.GET or None, user=request.user)
    if form.is_valid():
        producto = form.cleaned_data.get('producto')
        fecha_inicio = form.cleaned_data.get('fecha_inicio')
        fecha_fin = form.cleaned_data.get('fecha_fin')

        if producto:
            # Asegúrate de que el producto pertenece al usuario
            if producto.user == request.user:
                ventas = ventas.filter(producto=producto)
            else:
                ventas = ventas.none()  # No hay ventas si el producto no pertenece al usuario

        if fecha_inicio and fecha_fin:
            ventas = ventas.filter(fecha_venta__range=[fecha_inicio, fecha_fin])

    # Paginación
    paginator = Paginator(ventas, 10)  # 10 ventas por página
    page_number = request.GET.get('page')  # Obtener el número de página de la consulta
    try:
        ventas_paginated = paginator.page(page_number)
    except PageNotAnInteger:
        # Si no es un número entero, mostrar la primera página
        ventas_paginated = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página
        ventas_paginated = paginator.page(paginator.num_pages)

    return render(request, 'ventas/listar_ventas.html', {'ventas': ventas_paginated, 'form': form})
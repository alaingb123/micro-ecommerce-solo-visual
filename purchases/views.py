# Create your views here.
import random
import stripe
from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from carro.carro import Carro
from extra.models import Destinatario
from products.models import Product
from usuario.decorator import role_required
from .form import SolicitudZelleForm
from .models import Solicitud, SolicitudItem


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags





def buy_cart_solicitud(request,destinatario_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes estar registrado para poder realizar compras.')
        return HttpResponseRedirect(reverse('usuario:login'))



    if request.method == 'POST':
        destinatario = get_object_or_404(Destinatario, pk=destinatario_id)



    total = 0
    if not request.method == "POST":
        return HttpResponseBadRequest()

    purchase = Solicitud.objects.create(user=request.user)
    request.session['purchase_id'] = purchase.id
    if destinatario:
        if destinatario.nombre:
            purchase.nombre = destinatario.nombre
        if destinatario.apellidos:
            purchase.apellidos = destinatario.apellidos
        if destinatario.telefono:
            purchase.telefono = destinatario.telefono
        if destinatario.carnet_de_identidad:
            purchase.carnet_de_identidad = destinatario.carnet_de_identidad
        if destinatario.correo_electronico:
            purchase.correo_electronico = destinatario.correo_electronico
        if destinatario.direccion:
            purchase.direccion = destinatario.direccion
        if destinatario.municipio:
            purchase.municipio = destinatario.municipio
        if destinatario.instrucciones_entrega:
            purchase.instrucciones_entrega = destinatario.instrucciones_entrega


    session = request.session
    carro = session.get('carro', {})

    if not carro:
        return HttpResponseBadRequest("El carrito está vacío.")

    cart_items = carro.items()
    stock_error_products = []
    line_items = []
    for item_id, item in cart_items:
        product = get_object_or_404(Product, pk=item["product_id"])
        line_items.append({
            "price": product.price,
            "quantity": item["cantidad"],
        })
        if product.supply < item["cantidad"]:
            stock_error_products.append(product.name)

    if stock_error_products:
        stock_error = "Lo sentimos, no hay suficiente disponibilidad de los siguientes productos: " + ", ".join(
            stock_error_products) + ". Te recomendamos que los retires del carrito para continuar con tu compra."
        context = {
            "stock_error": stock_error
        }
        return render(request, "purchases/cart.html", context)
    else:
        stock_error = None




    for item_id, item in cart_items:
        product = get_object_or_404(Product, pk=item["product_id"])
        purchase.product.add(product)
        purchase.guardar_producto(product=product, quantity=item["cantidad"], purchase=purchase)
        total = total + item["subtotal"]

    purchase.stripe_price = total
    purchase.save()


    return redirect('purchases:success_cart')



@login_required
def view_solicitud_zelle(request, id_solicitud):
    solicitud = get_object_or_404(Solicitud, id=id_solicitud)

    # Check if the user has permission to view the solicitud
    if request.user != solicitud.user and request.user.usuario.rol.nombre != 'admin':
        return render(request, 'error.html', {'error_message': 'No tienes permiso para ver esta solicitud.'}, status=403)

    # Get the SolicitudZelleItem objects associated with the solicitud

    solicitud_items = SolicitudItem.objects.filter(solicitud=solicitud)



    context = {
        'solicitud': solicitud,
        'solicitud_items': solicitud_items,
    }

    return render(request, 'purchases/ver_solicitud_zelle.html', context)



@login_required
def solicitud_list(request):
    # Obtener los parámetros de filtro de la solicitud

    filter_usuario = request.GET.get('usuario' or None)

    if request.user.usuario.rol.nombre == 'admin':



        # Filtrar las solicitudes en base a los parámetros
        if filter_usuario:
            solicitudes = Solicitud.objects.filter(user__username__icontains=filter_usuario)
        else:
            solicitudes = Solicitud.objects.all()
    else:
        solicitudes = Solicitud.objects.filter(user=request.user)



    filter_estado = request.GET.get('estado')
    if filter_estado:
        solicitudes = solicitudes.filter(status=filter_estado)
    else:
        solicitudes = solicitudes.order_by('-status', '-id')

    # Paginar las solicitudes
    page_size = 20  # Número de solicitudes por página
    paginator = Paginator(solicitudes, page_size)
    page_number = request.GET.get('page', 1)

    try:
        page_solicitudes = paginator.page(page_number)
    except PageNotAnInteger:
        page_solicitudes = paginator.page(1)
    except EmptyPage:
        page_solicitudes = paginator.page(paginator.num_pages)



    context = {
        'solicitudes': page_solicitudes,
        'filter_usuario': filter_usuario,
        'filter_estado': filter_estado
    }
    return render(request, 'purchases/solicitud_list.html', context)


@role_required(['admin'])
def aceptar_solicitud(request,id_solicitud):
    solicitud = get_object_or_404(Solicitud, id=id_solicitud)
    solicitud.accept()
    print("se acepto la solicitud")

    context = {
        "id": id_solicitud,
    }
    html_message = render_to_string('purchases/email/solicitud_aceptada.html', context)
    plain_message = strip_tags(html_message)
    subject_email = "Solicitud de compra con E-commerce aceptada con éxito"
    user_email = solicitud.correo_electronico

    send_mail(
        subject=subject_email,
        message=plain_message,
        from_email=EMAIL_HOST_USER,
        recipient_list=[user_email],
        html_message=html_message,
        fail_silently=False,
    )
    print("se mando el email")
    return redirect('purchases:solicitud_list')


@role_required(['admin'])
def cancelar_solicitud(request,id_solicitud):
    solicitud = get_object_or_404(Solicitud, id=id_solicitud)

    context = {
        "id": id_solicitud,
    }
    html_message = render_to_string('purchases/email/solicitud_rechazada.html', context)
    plain_message = strip_tags(html_message)
    subject_email = "Solicitud de compra con E-commerce rechazada"
    user_email = solicitud.email

    send_mail(
        subject=subject_email,
        message=plain_message,
        from_email=EMAIL_HOST_USER,
        recipient_list=[user_email],
        html_message=html_message,
        fail_silently=False,
    )

    solicitud.cancel()
    return redirect('purchases:solicitud_list')



# def buy_cart(request,destinatario_id):
#     if not request.user.is_authenticated:
#         messages.warning(request, 'Debes estar registrado para poder realizar compras.')
#         return HttpResponseRedirect(reverse('usuario:login'))
#
#     if request.method == 'POST':
#         destinatario = get_object_or_404(Destinatario, pk=destinatario_id)
#
#     total = 0
#     if not request.method == "POST":
#         return HttpResponseBadRequest()
#
#     purchase = Solicitud.objects.create(user=request.user)
#     request.session['purchase_id'] = purchase.id
#     if destinatario:
#         if destinatario.nombre:
#             purchase.nombre = destinatario.nombre
#         if destinatario.apellidos:
#             purchase.apellidos = destinatario.apellidos
#         if destinatario.telefono:
#             purchase.telefono = destinatario.telefono
#         if destinatario.carnet_de_identidad:
#             purchase.carnet_de_identidad = destinatario.carnet_de_identidad
#         if destinatario.correo_electronico:
#             purchase.correo_electronico = destinatario.correo_electronico
#         if destinatario.direccion:
#             purchase.direccion = destinatario.direccion
#         if destinatario.municipio:
#             purchase.municipio = destinatario.municipio
#         if destinatario.instrucciones_entrega:
#             purchase.instrucciones_entrega = destinatario.instrucciones_entrega
#
#
#     session = request.session
#     carro = session.get('carro', {})
#
#     if not carro:
#         return HttpResponseBadRequest("El carrito está vacío.")
#
#     cart_items = carro.items()
#     stock_error_products = []
#     line_items = []
#
#     for item_id, item in cart_items:
#         product = get_object_or_404(Product, pk=item["product_id"])
#         purchase.product.add(product)
#         purchase.guardar_producto(product=product, quantity=item["cantidad"], purchase=purchase)
#         total = total + item["subtotal"]
#
#     purchase.stripe_price = total
#     purchase.save()
#
#     return redirect('solicitud_list')



def purchase_success_cart_view(request):
    purchase_id = request.session.get("purchase_id")
    session = request.session
    carro = session.get('carro', {})
    cart_items = carro.items()


    for item_id, item in cart_items:
        product = get_object_or_404(Product, pk=item["product_id"])
        product.supply = product.supply - item["cantidad"]
        product.save()


    carro = Carro(request)
    carro.limpiar_carro()

    if purchase_id:
        purchase = Solicitud.objects.get(id=int(purchase_id))
        purchase.completed = True
        purchase.save()
        del request.session['purchase_id']

        # Enviar email al usuario si tiene
        if purchase.user.email:
            context = {
                "total": purchase.stripe_price,
                "products": purchase.items.all(),
            }
            html_message = render_to_string('purchases/email/pago_con_exito_stripe.html', context)
            plain_message = strip_tags(html_message)
            subject_email = "Pago efectuado con exito"
            user_email = purchase.user.email

            send_mail(
                subject=subject_email,
                message=plain_message,
                from_email=EMAIL_HOST_USER,
                recipient_list=[user_email],
                html_message=html_message,
                fail_silently=False,
            )
        return HttpResponseRedirect(reverse("purchases:purchases_stripe"))
    return HttpResponseRedirect(reverse("products:list"))



@login_required
def pedidos_stripe(request):
    filter_usuario = request.GET.get('usuario' or None)
    if request.user.usuario.rol.nombre == 'admin':
        # Filtrar las solicitudes en base a los parámetros
        if filter_usuario:
            solicitudes = Solicitud.objects.filter(user__username__icontains=filter_usuario)
        else:
            solicitudes = Solicitud.objects.all()
    else:
        solicitudes = Solicitud.objects.filter(user=request.user)

    entrega = request.GET.get('estado' or None)
    if entrega:
        solicitudes = solicitudes.filter(entrega=entrega)

    solicitudes = solicitudes.order_by('-timestamp')

    completado = request.GET.get('completado' or None)


    if completado:
        if completado == 'false':
            solicitudes = solicitudes.filter(completed=False)
        else:
            solicitudes = solicitudes.filter(completed=True)
    else:
        solicitudes = solicitudes.filter(completed=True)




    # Paginar las solicitudes
    page_size = 20  # Número de solicitudes por página
    paginator = Paginator(solicitudes, page_size)
    page_number = request.GET.get('page', 1)

    try:
        page_solicitudes = paginator.page(page_number)
    except PageNotAnInteger:
        page_solicitudes = paginator.page(1)
    except EmptyPage:
        page_solicitudes = paginator.page(paginator.num_pages)



    context = {
        'pedidos_stripe': page_solicitudes,
        'filter_usuario': filter_usuario,
    }
    return render(request, 'purchases/solicitud_list.html', context)



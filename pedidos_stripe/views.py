# Create your views here.
import random
import stripe
from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from carro.carro import Carro
from extra.models import Destinatario
from products.models import Product
from usuario.decorator import role_required
from .models import Purchase, SolicitudStripeItem

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.urls import reverse
from stripe.error import APIConnectionError
import stripe






BASE_ENDPOINT= "http://127.0.0.1:8000"


cantidad = 0




def buy_cart_stripe(request,destinatario_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes estar registrado para poder realizar compras.')
        return HttpResponseRedirect(reverse('usuario:login'))

    if request.method == 'POST':
        destinatario = get_object_or_404(Destinatario, pk=destinatario_id)


    total = 0
    if not request.method == "POST":
        return HttpResponseBadRequest()

    purchase = Purchase.objects.create(user=request.user)
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

    return HttpResponseRedirect(reverse("pedidos_stripe:success_cart"))


@login_required
def pedidos_stripe(request):
    filter_usuario = request.GET.get('usuario' or None)
    if request.user.usuario.rol.nombre == 'admin':
        # Filtrar las solicitudes en base a los parámetros
        if filter_usuario:
            solicitudes = Purchase.objects.filter(user__username__icontains=filter_usuario)
        else:
            solicitudes = Purchase.objects.all()
    else:
        solicitudes = Purchase.objects.filter(user=request.user)

    entrega = request.GET.get('estado' or None)
    if entrega:
        solicitudes = solicitudes.filter(entrega=entrega)

    solicitudes = solicitudes.order_by('-created_at')

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



@login_required
def purchase_detail(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    if purchase.user != request.user and request.user.usuario.rol.nombre != 'admin':
        messages.warning(request, 'No tiene acceso a ese pedido')
        return HttpResponseRedirect(reverse('pedidos_stripe:purchases_stripe'))
    solicitud_items = SolicitudStripeItem.objects.filter(solicitud=purchase)


    context = {
        'purchase': purchase,
        'solicitud_items': solicitud_items,
    }

    return render(request, 'purchases/solicitud/solicitud_stripe_detail.html', context)



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
        purchase = Purchase.objects.get(id=int(purchase_id))
        purchase.completed = True
        purchase.save()
        del request.session['purchase_id']

        # Enviar email al usuario si tiene
        if purchase.correo_electronico:

            context = {
                "total": purchase.stripe_price,
                "products": purchase.items.all(),
            }
            html_message = render_to_string('purchases/email/pago_con_exito_stripe.html', context)
            plain_message = strip_tags(html_message)
            subject_email = "Compra efectuada con exito"
            user_email = purchase.correo_electronico

            send_mail(
                subject=subject_email,
                message=plain_message,
                from_email=EMAIL_HOST_USER,
                recipient_list=[user_email],
                html_message=html_message,
                fail_silently=False,
            )

            # Obtener todos los administradores
            admin_emails = User.objects.filter(usuario__rol__nombre='admin').values_list('email', flat=True)
            print(admin_emails)

            if admin_emails:
                admin_subject = "Nueva solicitud de compra"
                admin_context = {
                    "user_email": user_email,
                    "phone": purchase.telefono,
                    "total": purchase.stripe_price,
                    "products": purchase.items.all(),
                }
                admin_html_message = render_to_string('purchases/email/nueva_solicitud_admin.html', admin_context)
                admin_plain_message = strip_tags(admin_html_message)

                # Enviar correo a todos los administradores
                send_mail(
                    subject=admin_subject,
                    message=admin_plain_message,
                    from_email=EMAIL_HOST_USER,
                    recipient_list=list(admin_emails),  # Convertir a lista
                    html_message=admin_html_message,
                    fail_silently=False,
                )

        return HttpResponseRedirect(reverse("pedidos_stripe:purchases_stripe"))
    return HttpResponseRedirect(reverse("products:list"))



def purchase_stopped_view(request):
    purchase_id = request.session.get("purchase_id")
    if purchase_id:
        del request.session['purchase_id']
        return HttpResponseRedirect(reverse("products:list"))
    return HttpResponseRedirect(reverse("products:list"))



def purchase_success_view(request):
    purchase_id = request.session.get("purchase_id")


    if purchase_id:
        purchase = Purchase.objects.get(id=purchase_id)
        global cantidad
        product = purchase.product
        product.supply = product.supply - cantidad
        cantidad = 0
        product.save()
        purchase.completed = True
        purchase.save()
        del request.session['purchase_id']
        return HttpResponseRedirect(purchase.product.get_absolute_url())
    return HttpResponse(f"Finished {purchase_id}")


@role_required(['Proveedor'])
def ventas(request):
    ventas = SolicitudStripeItem.objects.filter(product__user=request.user,solicitud__completed=True)
    ventas = ventas.order_by('-solicitud__created_at')
    # Paginar los productos


    page_size = 20  # Número de solicitudes por página
    paginator = Paginator(ventas, page_size)
    page_number = request.GET.get('page', 1)

    try:
        page_solicitudes = paginator.page(page_number)
    except PageNotAnInteger:
        page_solicitudes = paginator.page(1)
    except EmptyPage:
        page_solicitudes = paginator.page(paginator.num_pages)



    context = {
        "ventas":page_solicitudes,
    }

    return render(request,'purchases/stripe/ventas.html',context)


@role_required(['Proveedor'])
def ver_venta(request,venta_id):
    venta = SolicitudStripeItem.objects.get(id=venta_id)
    if venta.product.user != request.user:
        messages.warning(request, 'No tiene acceso para esa venta')
        return HttpResponseRedirect(reverse('pedidos_stripe:ventas'))

    context = {
        "venta":venta
    }
    return render(request,'purchases/stripe/ver_venta.html',context)


@role_required(['admin'])
def aceptar_pedido(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    if purchase.entrega == 'pending':
        purchase.entrega = 'onway'

        try:
            purchase.save()
        except:
            pass

    context = {
        "id": purchase_id,
    }
    html_message = render_to_string('purchases/email/solicitud_aceptada.html', context)
    plain_message = strip_tags(html_message)
    subject_email = "Solicitud de compra con E-commerce aceptada con éxito"
    user_email = purchase.correo_electronico

    send_mail(
        subject=subject_email,
        message=plain_message,
        from_email=EMAIL_HOST_USER,
        recipient_list=[user_email],
        html_message=html_message,
        fail_silently=False,
    )

    return redirect('pedidos_stripe:ver_solicitud_stripe', purchase_id=purchase_id)


@role_required(['admin'])
def cancelar_pedido(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)

    if purchase.entrega == 'pending':
        purchase.entrega = 'canceled'
        purchase.save()

    return redirect('pedidos_stripe:ver_solicitud_stripe', purchase_id=purchase_id)



@role_required(['admin'])
def entregar_pedido(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)

    if purchase.entrega == 'onway':
        purchase.entrega = 'accepted'
        purchase.save()

    return redirect('pedidos_stripe:ver_solicitud_stripe', purchase_id=purchase_id)

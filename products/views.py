import requests
from django.core.checks import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
import mimetypes
from django.http import FileResponse, HttpResponseBadRequest, JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import  User
from stripe import APIConnectionError

from carro.carro import Carro
from extra.models import Promocion
from micro_ecommerce import settings

from usuario.decorator import role_required
# Create your views here.
from .form import ProductUpdateForm, ProductAttachmentInlineFormSet, ProductOfferForm, ProductForm
from .models import Product, ProductImage, ClasificacionPadre, ProductView, Rating, ProductOffer, Rating_product, Likes, \
    ClasificacionHija


from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta

from django.db import models



@role_required(['Proveedor'])
def product_create_view(request):
    context={}
    form = ProductForm(request.POST or None,  request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            clasi=int(request.POST.get('clasificacion'))
            obj = form.save(commit=False)
            clasificacion_hija = ClasificacionHija.objects.get(id=clasi)
            if request.user.is_authenticated:
                obj.user = request.user
                try:
                    obj.active = True
                    obj.save()
                    obj.clasificacion.add(clasificacion_hija)
                    obj.save()
                    if not hasattr(obj, 'rating_product'):
                        Rating_product.objects.create(product=obj)
                    form.save_m2m()
                except Exception as e:
                    # Manejo de otras excepciones
                    conexion_error =  f'Ocurrió un error inesperado: {str(e)}'
                    context = {
                        'conexion_error': conexion_error,
                        'form': form
                    }
                    return render(request, 'products/create.html', context)

                if request.POST.get('action') == 'save_and_add':
                    # Redirigir al mismo formulario para agregar otro producto
                    return redirect('products:create')
                else:
                    # Redirigir a otra página, por ejemplo, la lista de productos
                    return redirect(obj.get_manage_url())
            else:
                form.add_error(None,"Your  must be looged in to create product")
        else:
            conexion_error = form.errors

            context['conexion_error'] = conexion_error
    context['form'] = form
    return render(request, 'products/create.html',context)


from django.core.serializers import serialize

# @cache_page(60 * 15)  # 15 minutos
def product_list_view(request,provider_id=None,promotion_id=None):
    filtrado = False
    object_list = Product.objects.all()
    descuento = request.GET.get('descuento')
    if descuento:
        filtrado=True
        object_list = Product.objects.filter(offer__is_active=True)

    object_list = object_list.filter(active=True)

    no_nuevos=False



    # productos mas vendidos
    # top_products = (
    #     Product.objects.filter(active=True).annotate(total_sold=Sum('solicitudstripeitem__quantity'))
    #     .order_by('-total_sold')[:10]
    # )
    #------------------------------------------------------------------------------





    # ---------------------------------------------------------------




    # ofertas premuim
    premium_offer = ProductOffer.objects.filter(is_premium=True,is_active=True)
    # ---------------------------------------------------------------

    # productos mejor evaluados
    top_rated = Product.objects.filter(active=True).order_by('-rating_product__average_rating')[:10]
    # ---------------------------------------------------------------

    # productos nuevos
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=7)
    new_products = Product.objects.filter(timestamp__gte=seven_days_ago,active=True)[:10]

    # productos gustados por el usuario
    if not new_products.exists():
        # Si no hay productos nuevos, obtiene el top 5 de los productos con más likes
        new_products = Product.objects.filter(active=True).annotate(
            like_count=models.Count('like')
        ).order_by('-like_count')[:10]
        no_nuevos=True
    else:
        pass
    # ---------------------------------------------------------------



    promociones = Promocion.objects.all()

    # filtrar por la promocion
    if promotion_id:
        filtrado=True
        promotion = get_object_or_404(Promocion, id=promotion_id)
        object_list = promotion.productos.filter(active=True)
    # ------------------------------------------------------------



    # Obtener los productos y contar las vistas de la última semana
    week_ago = timezone.now() - timedelta(days=7)
    trending_products = (
        Product.objects.annotate(
            view_count=models.Count('productview', filter=models.Q(productview__timestamp__gte=week_ago,active=True)))
        .order_by('-view_count')[:10]  # Limitar a los 10 más vistos
    )
    # ---------------------------------------------------------------

    if provider_id:
        filtrado=True
        obj = get_object_or_404(User, id=provider_id)
        object_list = object_list.filter(user=obj)

    classifications = ClasificacionPadre.objects.all()
    carro = Carro(request)




    # Handle search query
    search_query = request.GET.get('search')
    if search_query:
        filtrado=True
        object_list = object_list.filter(keywords__icontains=search_query)

    # Handle classification filter
    classification_id = request.GET.get('classification_id')
    if classification_id:
        filtrado=True
        object_list = object_list.filter(clasificacion__id=classification_id)

    liked = request.GET.get('liked_product')
    if liked:
        filtrado=True
        object_list = Product.objects.filter(like__user=request.user)

    classification_id_padre = request.GET.get('classification_id_padre')
    if classification_id_padre:
        filtrado=True
        object_list = object_list.filter(clasificaciones_padre__id=classification_id_padre)






    # # Paginar los productos
    # page_size = 20  # Número de solicitudes por página
    # paginator = Paginator(object_list, page_size)
    # page_number = request.GET.get('page', 1)
    #
    # try:
    #     page_solicitudes = paginator.page(page_number)
    # except PageNotAnInteger:
    #     page_solicitudes = paginator.page(1)
    # except EmptyPage:
    #     page_solicitudes = paginator.page(paginator.num_pages)
    # products_data = serialize('json', object_list)


    context = {
        'object_list': object_list,
        'carro': carro,
        'classifications': classifications,
        'promociones': promociones,
        # 'top_products': top_products,
        'new_products': new_products,
        'trending_products': trending_products,
        'top_rated': top_rated,
        'premium_offer': premium_offer,
        'filtrado': filtrado,
        'no_nuevos': no_nuevos,

    }
    return render(request,"products/list.html",context)




@role_required(['Proveedor'])
def product_manage_detail_view(request,handle=None):
    obj = get_object_or_404(Product,handle=handle)
    # attachments = ProductImage.objects.filter(product=obj)
    is_manager = False

    if request.user.is_authenticated:
        is_manager = obj.user == request.user
    context = {"object": obj}

    if not is_manager:
        return HttpResponseBadRequest("No eres proveedor de este producto")
    form = ProductUpdateForm(request.POST or None,  request.FILES or None, instance=obj)

    # formset = ProductAttachmentInlineFormSet(request.POST or None,request.FILES or None,queryset=attachments)
    if request.method == 'POST':
        clasi = int(request.POST.get('clasificacion'))
        clasificacion_hija = ClasificacionHija.objects.get(id=clasi)
        if form.is_valid():
            instance = form.save(commit=False)
            print("el form es valido")
            try:
                instance.save()
                instance.clasificacion.clear()
                instance.clasificacion.add(clasificacion_hija)
                instance.save()
                form.save_m2m()  # Guarda las relaciones ManyToMany
            except APIConnectionError:
                # Manejo de error de conexión con Stripe
                conexion_error = 'Error de conexión con Stripe. Por favor, intenta más tarde.'
                context = {
                    'conexion_error': conexion_error,
                    'form': form,
                    # 'formset': formset,
                }
                return render(request, 'products/manager.html', context)

            except Exception as e:
                # Manejo de otras excepciones
                conexion_error = f'Ocurrió un error inesperado: {str(e)}'
                context = {
                    'conexion_error': conexion_error,
                    'form': form,
                    # 'formset': formset,
                }
                return render(request, 'products/manager.html', context)

            # formset.save(commit=False)
            # for _form in formset:
            #
            #     is_delete = _form.cleaned_data.get("DELETE")
            #
            #     try:
            #         attachments_obj = _form.save(commit=False)
            #     except:
            #         attachments_obj = None
            #     if is_delete:
            #         if attachments_obj is not None:
            #            if attachments_obj.pk:
            #                attachments_obj.delete()
            #     else:
            #         if attachments_obj is not None:
            #             attachments_obj.product = instance
            #             attachments_obj.save()


            return redirect(obj.get_manage_url())
        else:
            conexion_error = form.errors
            context['conexion_error'] = conexion_error
        context['form'] = form
        # context['formset'] = formset
    try:
        hija = obj.clasificacion.first().pk
        context['hija'] = hija
    except:
        pass
    try:
        padre = obj.clasificaciones_padre.pk
        print(padre)
        context['padre'] = padre
    except:
        pass
    context['form'] = form
    return render(request, 'products/manager.html', context)

def product_detail_view(request,handle=None):
    obj = get_object_or_404(Product,handle=handle)
    user_rating = None
    if obj.active == False:
        return redirect('products:list')
    attachments = ProductImage.objects.filter(product=obj)
    if request.user.is_authenticated:
        print("el rol es ",request.user.usuario.rol.nombre)
        if request.user.usuario.rol.nombre == "cliente":
            print("entro")
            ProductView.objects.create(product=obj, user=request.user)
            rating_product = get_object_or_404(Rating_product, product=obj)
            try:
                user_rating = Rating.objects.get(average=rating_product, user=request.user)
            except Rating.DoesNotExist:
                user_rating = None
    # attachments = obj.productattachment_set.all()
    is_owner = False

    if request.user.is_authenticated:
        is_owner = True # verify ownership



    context = {
        "object": obj,
        "is_owner": is_owner,
        "attachments":attachments,
        "user_rating":user_rating,
    }

    return render(request, 'products/detail.html', context)


def product_attachment_download_view(request,handle=None,pk=None):
    attachment = get_object_or_404(ProductImage,product__handle=handle,pk=pk)
    can_download = attachment.is_free or False
    if request.user.is_authenticated:
        can_download = True # check ownership
    if can_download is False:
        return HttpResponseBadRequest
    file=attachment.file.open(mode='rb') # cdn -> 53 object storage
    filename = attachment.file.name
    content_type, _encoding = mimetypes.guess_type(filename)
    response = FileResponse(file)
    response['Conten-Type'] = content_type or 'application/octet-stream'
    response['Content-Disposition'] = f'attachment;filename={filename}'
    return response


@role_required(['Proveedor'])
def mis_productos_table(request):
    today = timezone.now().date()
    carro = Carro(request)

    productos = Product.objects.filter(user=request.user)

    # Paginar los productos
    page_size = 20 # Número de solicitudes por página
    paginator = Paginator(productos, page_size)
    page_number = request.GET.get('page', 1)

    try:
        page_solicitudes = paginator.page(page_number)
    except PageNotAnInteger:
        page_solicitudes = paginator.page(1)
    except EmptyPage:
        page_solicitudes = paginator.page(paginator.num_pages)



    # ventas = SolicitudStripeItem.objects.filter(product__in=productos,solicitud__completed=True)

    # total_sales = ventas.aggregate(
    #     total=Sum('total_price')
    # )['total'] or 0

    product_sales = {}
    product_quantities = {}
    ventas_dia= {}

    # for product in productos:
    #     #ingreso total de las ventasd de un producto
    #     product_ventas = SolicitudStripeItem.objects.filter(product=product, solicitud__completed=True).aggregate(
    #         total_price=Sum('total_price')
    #     )
    #     #cantidad de productos vendidos
    #     product_cantidad = SolicitudStripeItem.objects.filter(product=product, solicitud__completed=True).aggregate(
    #         quantity=Sum('quantity')
    #     )
    #
    #
    #     product_sales[product.id] = product_ventas['total_price'] or 0
    #     product_quantities[product.id] = product_cantidad['quantity'] or 0

    for product in page_solicitudes:
        product.total_sales = product_sales.get(product.id, 0)
        product.cantidad = product_quantities.get(product.id, 0)

        # promedio de ventas al dia de un producto
        days_in_circulation = int((today - product.timestamp.date()).days)
        try:
            ventas_por_dias = product.cantidad / days_in_circulation
        except:
            ventas_por_dias = 0

        product.ventas_dia = ventas_por_dias

        # promedio de ventas por mes
        try:
            meses_en_circulacion = days_in_circulation/30
        except:
            meses_en_circulacion=0
        try:
            if meses_en_circulacion < 1:
                meses_en_circulacion=1
            ventas_mes = product.cantidad / meses_en_circulacion
        except:
            ventas_mes=0

        product.ventas_mes = ventas_mes

        try:
            porcentaje = (ventas_mes * 100) / product.supply
        except:
            porcentaje = 0

        product.porcentaje = int(porcentaje)

    context = {
        'productos': page_solicitudes,
        'carro': carro,
        # 'total_sales': total_sales,
    }
    return render(request, 'products/mis_productos_table.html',context)



# def get_monthly_sales(product):
#     today = timezone.now().date()
#     start_of_month = datetime(today.year, today.month, 1).date()
#     monthly_sales = SolicitudStripeItem.objects.filter(
#         product=product,
#         solicitud__completed=True,
#         solicitud__timestamp__date__gte=start_of_month
#     ).aggregate(
#         total_quantity=Sum('quantity')
#     )
#     print(monthly_sales["total_quantity"])
#     return monthly_sales

#
# @csrf_exempt
# @role_required(['Proveedor'])
# def delete_product(request):
#     if request.method == 'POST':
#         product_id = int(request.POST.get('product_id'))
#         try:
#             product = Product.objects.get(pk=product_id)
#             product.delete()
#             return HttpResponseRedirect('products:mis_productos')
#         except Product.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Product not found'})
#     else:
#         return JsonResponse({'success': False})


@csrf_exempt
def search(request):
  if request.method == 'POST':
    search_term = request.POST.get('search_term', '').lower()
    category = request.POST.get('category')

    # Realiza la consulta a la base de datos
    productos = Product.objects.filter(
      name__icontains=search_term,
    )

    # Convierte los resultados a un formato JSON
    context = {
        "productos":productos,
    }

    return JsonResponse(context, safe=False)

  return render(request, 'products/mis_productos_table.html')

@role_required(['Proveedor'])
def crear_oferta(request, product_id):
    product = Product.objects.get(id=product_id)

    if request.user != product.user:
        print("el usuairo es diferente")
        return redirect('products:detail', handle=product.handle)

    try:
        if product.offer:
            print("el producto ya tiene oferta ")
            return redirect('products:detail', handle=product.handle)
    except:
        pass


    if request.method == 'POST':
        form = ProductOfferForm(request.POST)
        if form.is_valid():
            oferta = form.save(commit=False)
            oferta.product = product
            oferta.precio_viejo = product.price
            oferta.save()
            oferta.is_offer_active()
            print("se creo la oferta")
            return redirect('products:detail', handle=product.handle)
        else:
            print("Errores en el formulario:", form.errors)
    else:
        form = ProductOfferForm()

    return render(request, 'products/oferta/crear_oferta.html', {'form': form,'product':product})

@role_required(['Proveedor'])
def eliminar_oferta(request,product_id):
    product = Product.objects.get(id=product_id)
    print(product)
    if request.method == 'POST':
        print("el metodo es post")
        if request.user == product.user:
            print("el usuario es el que es")
            try:
                print("la oferta se va a eliminar")
                product.offer.eliminar_oferta()
            except:
                print("la oferta no se elimino")
                return redirect('products:detail', handle=product.handle)
        else:
            return redirect('products:detail', handle=product.handle)
    return redirect('products:detail', handle=product.handle)



@role_required(['cliente'])
def rate_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)

        # secret_key = settings.RECAPTCHA_SECRET_KEY
        #
        # # captcha verification
        # data = {
        #     'response': request.POST.get('g-recaptcha-response'),
        #     'secret': secret_key
        # }
        # resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        # result_json = resp.json()
        #
        # print(result_json)
        #
        # if not result_json.get('success'):
        #     return redirect('products:detail', handle=product.handle)
        # # end captcha verification


        rating_product = product.rating_product

        score = int(request.POST.get('score'))

        rating, created = Rating.objects.update_or_create(
            average=rating_product,
            user=request.user,
            defaults={'score': score}
        )

        rating_product.update_average_rating()

        messages = 'Tu calificación ha sido registrada.'


        return redirect('products:detail', handle=product.handle)

    return HttpResponse(status=405)


@role_required(['cliente'])
def like_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    # Verificar si el usuario ya dio like al producto
    like, created = Likes.objects.get_or_create(user=user, product=product)

    if created:
        return JsonResponse({'message': 'Producto añadido a gustados'}, status=200)
    else:
        return JsonResponse({'message': 'Ya has dado like a este producto'}, status=400)

@role_required(['cliente'])
def dislike_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    try:
        like = Likes.objects.get(user=user, product=product)
        like.delete()  # Eliminar el like del usuario para el producto
        return JsonResponse({'message': 'Producto quitado de gustados'}, status=200)
    except Likes.DoesNotExist:
        return JsonResponse({'message': 'No has dado like a este producto'}, status=400)






def get_hijas(request):
    padre_id = request.GET.get('padre_id')
    hijas = ClasificacionHija.objects.filter(padre_id=padre_id).values('id', 'nombre')
    print(hijas)# Cambia 'nombre' por el campo adecuado
    return JsonResponse(list(hijas), safe=False)

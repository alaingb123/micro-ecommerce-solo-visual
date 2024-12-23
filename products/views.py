import os

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
from .models import Product, ProductImage, ProductView, Rating, ProductOffer, Rating_product, Likes, \
     Venta, Category

from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from django.db import models



@role_required(['Proveedor'])
def product_create_view(request):
    context={}
    clasificacion_hija = None
    form = ProductForm(request.POST or None,  request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                clasi = int(request.POST.get('clasificacion'))
            except:
                clasi = None
            try:
                clasi2 = int(request.POST.get('category'))
            except:
                clasi2 = None
            obj = form.save(commit=False)
            if request.user.is_authenticated:
                obj.user = request.user
                try:
                    obj.active = True
                    if clasi:
                        new_category = get_object_or_404(Category, id=clasi)
                        print(new_category)
                    else:
                        new_category = get_object_or_404(Category, id=clasi2)
                    obj.category = new_category

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


    top_productos = sorted(object_list, key=lambda p: p.total_ventas(), reverse=True)[:5]
    # ------------------------------------------------------------------------------





    # ---------------------------------------------------------------




    # ofertas premuim
    premium_offer = ProductOffer.objects.filter(is_premium=True,is_active=True)
    premium_offer = sorted(premium_offer, key=lambda offer: offer.product.count_views(), reverse=True)
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

    category = Category.get_root_nodes()
    carro = Carro(request)
    category = sorted(category, key=lambda x: x.search_count, reverse=True)




    # Handle search query
    search_query = request.GET.get('search')
    if search_query:
        filtrado=True
        object_list = object_list.filter(
            Q(keywords__icontains=search_query) | Q(name__icontains=search_query)
        )

    # Handle classification filter
    classification_id = request.GET.get('category')
    if classification_id:
        filtrado = True
        # Obtener la categoría seleccionada
        categoria_seleccionada = Category.objects.get(pk=classification_id)
        categoria_seleccionada.increment_search_count()
        print(categoria_seleccionada.search_count)
        # Filtrar los productos por la categoría y sus descendientes
        descendants = categoria_seleccionada.get_descendants()
        object_list1 = object_list.filter(category__in=descendants)
        object_list2 = object_list.filter(category=categoria_seleccionada)
        object_list = object_list1.union(object_list2)

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


    for cate in category:
        # Contar productos en la categoría y sus subcategorías
        cate.product_count = (
                cate.products.count() +
                cate.get_children().aggregate(total=Count('products'))['total'] or 0
        )
    # Ordenar el object_list por el conteo de vistas
    object_list = (
        Product.objects.filter(id__in=object_list.values_list('id', flat=True))
        .order_by('-views')  # Ordenar por el campo views
    )

    context = {
        'object_list': object_list[:50],
        'carro': carro,
        'category': category,
        'promociones': promociones,
        'top_products': top_productos,
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
    clasificacion_hija = None
    clasificacion_padre = None

    if request.user.is_authenticated:
        is_manager = obj.user == request.user
    context = {"object": obj}

    if not is_manager:
        return HttpResponseBadRequest("No eres proveedor de este producto")
    form = ProductUpdateForm(request.POST or None,  request.FILES or None, instance=obj)

    # formset = ProductAttachmentInlineFormSet(request.POST or None,request.FILES or None,queryset=attachments)
    if request.method == 'POST':
        if request.POST.get('category'):
            try:
                clasi = int(request.POST.get('clasificacion'))
                clasificacion_hija = get_object_or_404(Category, pk=clasi)
                # clasificacion_hija = root_category.get_children()
            except:
                clasificacion_hija = None

            try:
                clasi2 = int(request.POST.get('category'))

                clasificacion_padre = get_object_or_404(Category, pk=clasi2)
            except:
                clasificacion_padre = None

        if form.is_valid():

            instance = form.save(commit=False)
            if 'image' in request.FILES:
                # Si hay una imagen antigua y es diferente, eliminarla
                if instance.image and os.path.isfile(instance.image.path):
                    os.remove(instance.image.path)
            try:
                price_changed = instance.price != obj.offer.precio_viejo  # Compara el nuevo precio con el actual
                if price_changed and obj.offer:
                    context['conexion_error'] = 'Debes eliminar la oferta activa antes de cambiar el precio.'
                    context['form'] = form
                    return render(request, 'products/manager.html', context)
            except:
                pass
            try:
                instance.save()
                if clasificacion_hija:
                    instance.category = clasificacion_hija
                else:
                    instance.category = clasificacion_padre
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
    # try:
    #     hija = obj.clasificacion.first().pk
    #     context['hija'] = hija
    # except:
    #     pass
    try:
        if obj.category.get_parent():
            padre = obj.category.get_parent().pk
            context['padre'] = padre
            context['hija'] = obj.category.pk
        else:
            padre = obj.category.pk
            context['padre'] = padre

    except:
        pass
    context['form'] = form
    return render(request, 'products/manager.html', context)

def product_detail_view(request,handle=None):
    obj = get_object_or_404(Product,handle=handle)
    user_rating = None
    obj.views  = obj.views + 1
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
    total_sales = 0

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


    for product in page_solicitudes:
        # promedio de ventas al dia de un producto
        # print(product.total_ventas())
        total_sales= product.total_ingresos() + total_sales
        days_in_circulation = int((today - product.timestamp.date()).days)
        try:
            ventas_por_dias = product.total_ventas() / days_in_circulation
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
            ventas_mes = product.total_ventas() / meses_en_circulacion
        except:
            ventas_mes=0

        product.ventas_mes = ventas_mes

        try:
            porcentaje = (ventas_mes * 100) / product.supply
        except:
            porcentaje = 0

        product.porcentaje = int(porcentaje)
        print(product.ventas_dia)

    context = {
        'productos': page_solicitudes,
        'carro': carro,
        'total_sales': total_sales,
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

    if request.method == 'POST':

        if request.user == product.user:

            try:

                product.offer.eliminar_oferta()
            except:

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
    root_category = get_object_or_404(Category, pk=padre_id)
    child_categories = root_category.get_children()

    # Crear una lista de diccionarios para la respuesta JSON
    child_categories_data = [{'id': child.id, 'name': child.name} for child in child_categories]

    print(child_categories_data)
    return JsonResponse(child_categories_data, safe=False)


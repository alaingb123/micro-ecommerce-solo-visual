from extra.models import StoreSettings
from products.models import Product




def cantidad_like(request):
    if request.user.is_authenticated:
        liked_products = Product.objects.filter(like__user=request.user)
        cantidad_like = liked_products.count()
    else:
        cantidad_like=0

    settings = StoreSettings.get_instance()
    return {
        'cantidad_like': cantidad_like,
        'store_settings': settings
    }




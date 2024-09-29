from django.shortcuts import render

from carro.carro import Carro


def home_view(request):
    carro = Carro(request)
    subtotal=0
    context = {
        'carro': carro,
        'subtotal': subtotal
    }
    return render(request, "home.html",context)

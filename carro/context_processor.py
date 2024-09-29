


def importe_total_carro(request):
    importe_total = 0
    if 'carro' in request.session:
        for key, value in request.session['carro'].items():
            importe_total += float(value.get('subtotal', 0))
    return {'importe_total_carro': importe_total}




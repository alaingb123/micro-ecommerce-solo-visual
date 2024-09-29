from django.shortcuts import render

# Create your views here.
from django.contrib.sessions.models import Session

class Carro:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.carro = self.session.get('carro', {})

    def agregar(self, product,quantity):
        # print(quantity)
        if (str(product.pk) not in self.carro.keys()):
            self.carro[product.pk] = {
                "product_id": product.pk,
                "name": product.name,
                "price": float(product.price),
                "cantidad": quantity,
                "imagen": product.image.url,
                "subtotal":float(product.price * quantity)
            }
        else:
            for key, value in self.carro.items():
                if key == str(product.pk):
                    if value["cantidad"] < product.supply:
                        value["cantidad"] = value["cantidad"] + quantity
                        value["subtotal"] = float(value["subtotal"]) + float(product.price)
                        break
        self.guardar_carro()

    def guardar_carro (self):
        self.session["carro"] = self.carro
        self.session.modified = True

    def eliminar(self, product):
        product_id = str(product.pk)
        if product_id in self.carro:
            del self.carro[product_id]
            self.guardar_carro()

    def restar_product(self,product):
        for key, value in self.carro.items():
            if key == str(product.pk):
                value["cantidad"] = value["cantidad"] - 1
                value["subtotal"] = float(value["subtotal"]) - float(product.price)
                if value["cantidad"] < 1:
                    self.eliminar(product)
                break
        self.guardar_carro()


    def limpiar_carro(self):
        self.session["carro"]={}
        self.session.modified=True

    def obtener_cantidad_total(self):
        total_cantidad = sum(item['cantidad'] for item in self.carro.values())
        return total_cantidad

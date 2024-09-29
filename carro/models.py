from django.db import models

# Create your models here.

from django.shortcuts import render

# Create your views here.

class Carro:
    def __int__(self,request):
        self.request = request
        self.session = request.session
        try:
            carro = self.session.get("carro")
        except:
            if not carro:
                carro = self.session["carro"]={}
            else:
                self.carro = carro

    def agregar(self,product):
        if (str(product.pk) not in self.carro.keys()):
            self.carro[product.pk] = {
                "product_id": product.pk,
                "name": product.name,
                "precio": str(product.price),
                "cantidad":1,
                "imagen": product.image.url
            }
        else:
            for key,value in self.carro.items():
                if key == str(product.pk):
                    value["canitdad"] = value["cantidad"] + 1
                    break
        self.guardar_carro()

    def guardar_carro (self):
        self.session["carro"] = self.carro
        self.session.modified = True

    def eliminar(self, product):
        product.pk = str(product.pk)
        if product.pk in self.carro:
            del self.carro[product.pk]
            self.guardar_carro()

    def restar_product(self,product):
        for key, value in self.carro.items():
            if key == str(product.pk):
                value["canitdad"] = value["cantidad"] - 1
                if value["cantidad"] < 1:
                    self.eliminar(product)
                break
        self.guardar_carro()


    def limpiar_carro(self):
        self.session["carro"]={}
        self.session.modified=True

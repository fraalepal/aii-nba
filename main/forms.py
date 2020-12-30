#encoding:utf-8
from main.models import Posicion
from django import forms

class BusquedaPorPosicionForm(forms.Form):
    lista=[(g.id,g.posicionNombre) for g in Posicion.objects.all()]
    posicion = forms.ChoiceField(label="Seleccione la posicion", choices=lista)
#encoding:utf-8
from main.models import Noticia, Posicion
from django import forms

class BusquedaPorPosicionForm(forms.Form):
    lista=[(g.id,g.posicionNombre) for g in Posicion.objects.all()] #g.id cambiar a lo que se va a buscar para Whoosh
    posicion = forms.ChoiceField(label="Seleccione la posicion", choices=lista)

class BusquedaPorTituloForm(forms.Form):
    lista=[(g.titulo,g.titulo) for g in Noticia.objects.all()] #g.id cambiar a lo que se va a buscar para Whoosh
    titulo = forms.CharField(label='Introduce el texto a buscar  ', max_length=100)


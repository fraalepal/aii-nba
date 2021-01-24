#encoding:utf-8
from main.models import Equipo, Jugador, Noticia, Posicion, PosicionDraft
from django import forms

class BusquedaPorPosicionForm(forms.Form):
    lista=[(g.id,g.posicionNombre) for g in Posicion.objects.all()] #g.id cambiar a lo que se va a buscar para Whoosh
    posicion = forms.ChoiceField(label="Seleccione la posicion    ", choices=lista)

class BusquedaPorPosicionWHForm(forms.Form):
    lista=[(g.posicionNombre,g.posicionNombre) for g in PosicionDraft.objects.all()] 
    posicion = forms.ChoiceField(label="Seleccione la posicion", choices=lista)

class BusquedaPorPosicionJugadorWHForm(forms.Form):
    lista=[(g.posicionNombre,g.posicionNombre) for g in Posicion.objects.all()] 
    posicion = forms.ChoiceField(label="Seleccione la posicion", choices=lista)

class BusquedaPorEquipoWHForm(forms.Form):
    lista=[(g.nombreEquipo,g.nombreEquipo) for g in Equipo.objects.all()] #g.id cambiar a lo que se va a buscar para Whoosh
    equipo = forms.ChoiceField(label="Seleccione el equipo", choices=lista)

class BusquedaPorPosicionDraftForm(forms.Form):
    lista=[(g.id,g.posicionNombre) for g in PosicionDraft.objects.all()] #g.id cambiar a lo que se va a buscar para Whoosh
    posicion = forms.ChoiceField(label="Seleccione la posicion", choices=lista)

class BusquedaPorTituloForm(forms.Form):
    lista=[(g.titulo,g.titulo) for g in Noticia.objects.all()] #g.id cambiar a lo que se va a buscar para Whoosh
    titulo = forms.CharField(label='Introduce el texto a buscar  ', max_length=100)

class BusquedaPorNombreForm(forms.Form):
    lista=[(g.nombreJugador,g.nombreJugador) for g in Jugador.objects.all()] #g.id cambiar a lo que se va a buscar para Whoosh
    nombreJugador = forms.CharField(label='Introduce el nombre del jugador a buscar  ', max_length=100)

class EquipoForm(forms.Form):
    lista=[(g.nombreEquipo,g.nombreEquipo) for g in Equipo.objects.all()] #g.id cambiar a lo que se va a buscar para Whoosh
    equipo = forms.ChoiceField(label="Seleccione el equipo", choices=lista)

class FilmForm(forms.Form):
    lista=[(g.id,g.nombreJugador) for g in Jugador.objects.all()] #g.id cambiar a lo que se va a buscar para Whoosh
    id = forms.CharField(label='Introduce el nombre del jugador a buscar  ', max_length=100)

'''class RatingForm(forms.Form):
    user_id = forms.CharField(label='Usuario', max_length=100)
    ropa_id = forms.CharField(label='Ropa', max_length=100)
    valoracion = forms.ChoiceField(label="Valoracion", choices=((1, ('1')),(2, ('2')),(3, ('3')),(4, ('4')),(5, ('5'))))'''
    
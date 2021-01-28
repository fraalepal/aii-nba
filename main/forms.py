#encoding:utf-8
from main.models import Equipo, Jugador, Noticia, Posicion, PosicionDraft, Universidad
from django import forms

#Buscador por posicion de jugadores
class BusquedaPorPosicionForm(forms.Form):
    lista=[(g.id,g.posicionNombre) for g in Posicion.objects.all()] #g.id cambiar a lo que se va a buscar para Whoosh
    posicion = forms.ChoiceField(label="Seleccione la posicion    ", choices=lista)


#Buscador por posicion de jugadores actuales con whoosh
class BusquedaPorPosicionJugadorWHForm(forms.Form):
    lista=[(g.posicionNombre,g.posicionNombre) for g in Posicion.objects.all()] 
    posicion = forms.ChoiceField(label="Seleccione la posicion", choices=lista)

#Buscador por posicion de drafteados
class BusquedaPorPosicionDraftForm(forms.Form):
    lista=[(g.id,g.posicionNombre) for g in PosicionDraft.objects.all()] #g.id cambiar a lo que se va a buscar para Whoosh
    posicion = forms.ChoiceField(label="Seleccione la posicion", choices=lista)

#Buscador de jugador por nombre con whoosh
class BusquedaPorNombreForm(forms.Form):
    lista=[(g.nombreJugador,g.nombreJugador) for g in Jugador.objects.all()] #g.id cambiar a lo que se va a buscar para Whoosh
    nombreJugador = forms.CharField(label='Introduce el nombre del jugador a buscar  ', max_length=100)

#Buscador por posicion de drafteados con whoosh
class BusquedaPorPosicionWHForm(forms.Form):
    lista=[(g.posicionNombre,g.posicionNombre) for g in PosicionDraft.objects.all()] 
    posicion = forms.ChoiceField(label="Seleccione la posicion", choices=lista)

#Buscador por universidad de drafteados con whoosh
class BusquedaPorUniversidadWHForm(forms.Form):
    lista=[(g.nombreUniversidad,g.nombreUniversidad) for g in Universidad.objects.all()] 
    universidad = forms.ChoiceField(label="Seleccione la universidad", choices=lista)

#Buscador de jugadores por equipo con whoosh
class BusquedaPorEquipoWHForm(forms.Form):
    lista=[(g.nombreEquipo,g.nombreEquipo) for g in Equipo.objects.all()] #g.id cambiar a lo que se va a buscar para Whoosh
    equipo = forms.ChoiceField(label="Seleccione el equipo", choices=lista)


#Buscador de noticias por contenido por whoosh
class BusquedaPorTituloForm(forms.Form):
    lista=[(g.titulo,g.titulo) for g in Noticia.objects.all()] #g.id cambiar a lo que se va a buscar para Whoosh
    titulo = forms.CharField(label='Introduce el texto a buscar  ', max_length=100)

class JugadoresSimilaresForm(forms.Form):
    lista=[(g.id,g.nombreJugador) for g in Jugador.objects.all()] #g.id cambiar a lo que se va a buscar para Whoosh
    id = forms.CharField(label='Introduce el nombre del jugador a buscar  ', max_length=100)


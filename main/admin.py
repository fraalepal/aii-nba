from django.contrib import admin
from main.models import Equipo, Jugador, Drafteado, Noticia, Posicion, PosicionDraft, Puntuacion
#registramos en el administrador de django los modelos 

admin.site.register(Equipo)
admin.site.register(Jugador)
admin.site.register(Drafteado)
admin.site.register(Noticia)
admin.site.register(Posicion)
admin.site.register(PosicionDraft)
admin.site.register(Puntuacion)

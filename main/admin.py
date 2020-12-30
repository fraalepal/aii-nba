from django.contrib import admin
from main.models import Equipo, Jugador, Drafteado, Noticia, Posicion
#registramos en el administrador de django los modelos 

admin.site.register(Equipo)
admin.site.register(Jugador)
admin.site.register(Drafteado)
admin.site.register(Noticia)
admin.site.register(Posicion)
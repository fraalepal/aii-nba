#encoding:utf-8
from datetime import date, datetime
from django.contrib.auth.forms import UsernameField
from django.db import models
from django.contrib.auth.models import User

class Posicion(models.Model):
    posicionNombre = models.CharField(max_length=256, verbose_name='Posición')

    def __str__(self):
        return self.posicionNombre

class PosicionDraft(models.Model):
    posicionNombre = models.CharField(max_length=256, verbose_name='PosiciónDraft')

    def __str__(self):
        return self.posicionNombre

class Equipo(models.Model):
    logoEquipo = models.CharField(max_length=256, default="nul")
    nombreEquipo = models.CharField(max_length=64, primary_key=True, unique=False)
    ranking = models.CharField(max_length=256, default="nul")
    proxPartido = models.CharField(max_length=256, default="nul")
    estadisticas = models.CharField(max_length=256, default="nul")
    lesionados = models.CharField(max_length=256, default="nul")
    listaJugadores = models.CharField(max_length=512, default="nul")
    sumaSalarios = models.IntegerField(default=0)

    def __str__(self):
        return self.nombreEquipo



class Jugador(models.Model):
    imagenJugador = models.CharField(max_length=256, default="nul")
    nombreJugador = models.CharField(max_length=64, default="nul")
    posicionJugador = models.CharField(Posicion,max_length=64, default="nul")
    nombreEquipo = models.ForeignKey(Equipo,max_length=256, on_delete=models.DO_NOTHING)
    salarioNumero = models.IntegerField(default=0)
    puntosPorPartido = models.FloatField(default=0.0)
    asistenciasPorPartido = models.FloatField(default=0.0)
    rebotesPorPartido = models.FloatField(default=0.0)
    per = models.FloatField(default=0.0)

    def __str__(self):
        return self.nombreJugador

class Universidad(models.Model):
    nombreUniversidad = models.CharField(max_length=64, primary_key=True, unique=False)

    def __str__(self):
        return self.nombreUniversidad

class Drafteado(models.Model):
    nombreJugador = models.CharField(max_length=64, default="nul")
    posicionJugador = models.CharField(PosicionDraft,max_length=64, default="nul")
    universidad = models.CharField(Universidad,max_length=256, default="nul")
    pickJugador = models.IntegerField(default=0)

    def __str__(self):
        return self.nombreJugador



class Noticia(models.Model):
    imagenNoticia = models.CharField(max_length=256, default="nul")
    titulo = models.CharField(max_length=64, default="nul")
    enlace = models.CharField(max_length=256, default="nul")
    contenido = models.TextField(default="nul")

    def __str__(self):
        return self.titulo


class Puntuacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    valor = models.IntegerField()

    def __str__(self):
        return str(self.valor)
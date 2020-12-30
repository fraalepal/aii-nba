#encoding:utf-8
from django.db import models



    
class Equipo(models.Model):
    logoEquipo = models.CharField(max_length=256, default="nul")
    nombreEquipo = models.CharField(max_length=64)
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
    posicionJugador = models.CharField(max_length=256, default="Draft 2021")
    nombreEquipo = models.CharField(max_length=256, default="Draft 2021")
    salarioNumero = models.IntegerField(default=0)
    puntosPorPartido = models.FloatField(default=0.0)
    asistenciasPorPartido = models.FloatField(default=0.0)
    rebotesPorPartido = models.FloatField(default=0.0)

    def __str__(self):
        return self.nombreJugador

class Drafteado(models.Model):
    nombreJugador = models.CharField(max_length=64, default="nul")
    posicionJugador = models.CharField(max_length=256, default="nul")
    universidad = models.CharField(max_length=256, default="nul")
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
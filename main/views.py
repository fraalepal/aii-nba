#encoding:utf-8
from typing import Generic
from main.recommendations import getRecommendations,topMatches
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from main.forms import BusquedaPorEquipoWHForm, BusquedaPorNombreForm, BusquedaPorPosicionDraftForm, BusquedaPorPosicionForm, BusquedaPorPosicionJugadorWHForm, BusquedaPorPosicionWHForm, BusquedaPorTituloForm, JugadoresSimilaresForm
from main.models import Equipo, Jugador, Drafteado, Noticia, Posicion, PosicionDraft, Puntuacion
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from bs4 import BeautifulSoup
import urllib.request
import lxml
from datetime import date, datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login as do_login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.urls import reverse_lazy
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder

import os
from whoosh import qparser
from whoosh.fields import DATETIME, TEXT, ID, NUMERIC, Schema
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser, QueryParser

from django.db.models import Q

import shelve

#LISTADOS DE ELEMENTOS

def inicio(request):
    num_equipos=Equipo.objects.all().count()
    return render(request,'inicio.html', {'num_equipos':num_equipos})


def lista_equipos(request):
    equipos=Equipo.objects.all()
    return render(request,'equipos.html', {'equipos':equipos})

def lista_equipostest(request):
    equipostest=Equipo.objects.all()
    return render(request,'equipostest.html', {'equipostest':equipostest})

def lista_jugador(request):
    jugadores_list=Jugador.objects.all().order_by("nombreJugador")
    page = request.GET.get('page', 1)

    paginator = Paginator(jugadores_list, 30)
    try:
        jugadores = paginator.page(page)
    except PageNotAnInteger:
        jugadores = paginator.page(1)
    except EmptyPage:
        jugadores = paginator.page(paginator.num_pages)

    return render(request, 'jugadores.html', { 'jugadores': jugadores })


def lista_drafteados(request):
    drafteados_list=Drafteado.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(drafteados_list, 6)
    try:
        drafteados = paginator.page(page)
    except PageNotAnInteger:
        drafteados = paginator.page(1)
    except EmptyPage:
        drafteados = paginator.page(paginator.num_pages)

    return render(request, 'drafteados.html', { 'drafteados': drafteados })

def lista_noticias(request):
    noticias=Noticia.objects.all().order_by("-id")
    return render(request,'noticias.html', {'noticias':noticias})

#BUSQUEDAS CON SQLITE3

#Buscar mejores jugadores g-league por posicion
def buscar_jugadoresgleagueporposicion(request):
    formulario = BusquedaPorPosicionForm()
    jugadores = None
    
    if request.method=='POST':
        formulario = BusquedaPorPosicionForm(request.POST)      
        if formulario.is_valid():
            jugadores = Jugador.objects.filter(salarioNumero = 0).filter(posicionJugador = Posicion.objects.get(pk=formulario.cleaned_data['posicion'])).order_by("-puntosPorPartido")[:3]

    return render(request, 'buscargleagueporposicion.html', {'formulario':formulario, 'jugadoress':jugadores})

#Buscar jugadores lideres por posicion
def buscar_jugadores_lideres_por_posicion(request):
    formulario = BusquedaPorPosicionForm()
    jugador = None
    

    if request.method=='POST':
        formulario = BusquedaPorPosicionForm(request.POST)      
        if formulario.is_valid():
            jugador = Jugador.objects.filter(posicionJugador = Posicion.objects.get(pk=formulario.cleaned_data['posicion'])).order_by("-puntosPorPartido")[:5]

        

    return render(request, 'buscarjugadoreslideresporposicion.html', {'formulario': formulario, 'jugador': jugador})


#BUSQUEDAS WHOOSH
#Buscar noticias por palabra clave en contenido o titulo
def buscar_noticias_titulo(request):
    formulario = BusquedaPorTituloForm(request.POST)
    noticias = None 
    if formulario.is_valid():
        ix = open_dir("main_info/news")
        with ix.searcher() as searcher:
            titulo = formulario.cleaned_data['titulo']
            query = MultifieldParser(["titulo","contenido"], ix.schema).parse(str(titulo))
            noticias = []
            result = searcher.search(query, limit = 10)
            for r in result:
                aux = {"imagenNoticia" : r['imagenNoticia'], "titulo": r['titulo'], "enlace": r['enlace'], "contenido": r['contenido']}
                noticias.append(aux)
            print(noticias)

    return render(request, 'buscarnoticiasportitulo.html', {'formulario': formulario, 'noticias': noticias})

#Buscar jugadores actuales por nombres
def buscar_jugador_por_nombre(request):
    formulario = BusquedaPorNombreForm(request.POST)
    jugador = None 
    if formulario.is_valid():
        ix = open_dir("main_info/jugadores")
        with ix.searcher() as searcher:
            nombreJugador = formulario.cleaned_data['nombreJugador']
            query = MultifieldParser(["nombreJugador"], ix.schema).parse(str(nombreJugador))
            jugador = []
            result = searcher.search(query, limit = 10)
            for r in result:
                aux = {"imagenJugador" : r['imagenJugador'], "nombreJugador": r['nombreJugador'], "posicionJugador": r['posicionJugador'], "nombreEquipo": r['nombreEquipo'], "salarioNumero": r['salarioNumero'], "puntosPorPartido": r['puntosPorPartido'], "asistenciasPorPartido": r['asistenciasPorPartido'], "rebotesPorPartido": r['rebotesPorPartido'], "per": r['per'],"id": r['id']}
                jugador.append(aux)
            print(jugador)

    return render(request, 'buscarjugadorpornombre.html', {'formulario': formulario, 'jugador': jugador})

#Buscar jugadores actuales por equipos
def buscar_jugadores_por_equipo(request):
    formulario = BusquedaPorEquipoWHForm(request.POST)
    jugador = None 
    if formulario.is_valid():
        ix = open_dir("main_info/jugadores")
        with ix.searcher() as searcher:
            equipo = formulario.cleaned_data['equipo']
            query = MultifieldParser(["nombreEquipo"], ix.schema).parse(str(equipo))
            jugador = []
            result = searcher.search(query, limit = None)
            for r in result:
                aux = {"imagenJugador" : r['imagenJugador'], "nombreJugador": r['nombreJugador'], "posicionJugador": r['posicionJugador'], "nombreEquipo": r['nombreEquipo'], "salarioNumero": r['salarioNumero'], "puntosPorPartido": r['puntosPorPartido'], "asistenciasPorPartido": r['asistenciasPorPartido'], "rebotesPorPartido": r['rebotesPorPartido'], "per": r['per'], "id": r['id']}
                jugador.append(aux)
            print(jugador)
    return render(request, 'buscarjugadoresporequipo.html', {'formulario': formulario, 'jugador': jugador})

#Buscar drafteados por posición
def buscar_jugadores_drafteados_por_posicion(request):
    formulario = BusquedaPorPosicionWHForm(request.POST)
    drafteados = [] 
    if formulario.is_valid():
        ix = open_dir("main_info/drafteados")
        with ix.searcher() as searcher:
            posicion = str(formulario.cleaned_data['posicion'])
            query = MultifieldParser(["posicionJugador"], ix.schema).parse(posicion)
            result = searcher.search(query, limit = None)
            for r in result:
                aux = {"nombreJugador": r['nombreJugador'], "posicionJugador": r['posicionJugador'], "universidad": r['universidad'], "pickJugador": r['pickJugador']}
                drafteados.append(aux)
    return render(request, 'buscardrafteadosporposicion.html', {'formulario': formulario, 'drafteados': drafteados})


#GESTIÓN DE USUARIOS
#Función de registro de usuarios
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

#Función de cierre de sesión
def logout(request):
    # Finalizamos la sesión
    do_logout(request)
    # Redireccionamos a la portada
    return redirect('/')


#SISTEMA DE RECOMENDACIÓN
#Creación de votos para jugadores
@login_required
def insertarNuevaPuntuacion(request):
    mensaje ="Se ha votado correctamente"
    if request.method == 'POST':
        formulario = request.POST
        
        
        valor = formulario['valor']
        if(int(valor)>5):
            valor = "5"
        elif int(valor)<1:
            valor = "1"
        usuario = formulario['usuario']
        jugador = formulario['jugador']
        puntuaciones = Puntuacion.objects.all().filter(usuario=User(id=str(usuario))).filter(jugador=Jugador(id=str(jugador)))

        if(len(list(puntuaciones))==0):
            nuevaPuntuacion = Puntuacion()
            nuevaPuntuacion.valor = valor
            nuevaPuntuacion.usuario = User(id=str(usuario))
            nuevaPuntuacion.jugador = Jugador(id=str(jugador))
            nuevaPuntuacion.save()
            contadorPuntuaciones = Puntuacion.objects.count()
            print(contadorPuntuaciones) 
            
        else:
            puntuacionParaActualizar = puntuaciones[0]
            puntuacionParaActualizar.delete()
            puntuacionParaActualizar.valor = valor
            puntuacionParaActualizar.save()
    

    return render(request,'jugadores.html', {'mensaje': mensaje})                   

#Vista de jugadores ya puntuados por un usuario
@login_required
def misPuntuaciones(request):
    usuario = request.user
    puntuaciones = Puntuacion.objects.filter(usuario=request.user)
    jugadores = []
    valores = []
    for puntuacion in puntuaciones:
        n = puntuacion.valor
        valores.append(n)
        j = puntuacion.jugador
        jugadores.append(j)

    #totalpuntuaciones = serialize('json', puntuaciones)

    return render(request,'mispuntuaciones.html', {'jugadores': jugadores, 'valores': valores})

#Jugadores para fichar recomendados por otros usuarios
@login_required
def jugadoresRecomendadorPorUsuarios(request):
    if request.method=='GET':
        usuario = request.user
        rankings = getRecommendations(usuario)
        recommended = rankings[:5]
        jugadores = []
        valores = []
        for re in recommended:
            jugadores.append(Jugador.objects.get(pk=re[1]))
            valores.append(re[0])
        items= zip(jugadores,valores)

        return render(request,'fichajesRecomendadosPorUsuarios.html', {'usuario': usuario, 'items': items})

#Jugadores similares a otros
def jugadoresSimilares(request):
    jugador = None
    if request.method=='GET':
        form = JugadoresSimilaresForm(request.GET, request.FILES)
        if form.is_valid():
            idJugador = form.cleaned_data['id']
            jugador = get_object_or_404(Jugador, pk=idJugador)
            shelf = shelve.open("dataRS.dat")
            ItemsPrefs = shelf['Prefs']
            shelf.close()
            idJugador = jugador.id
            recommended = topMatches(ItemsPrefs, int(idJugador),n=3)
            jugadores = []
            similar = []
            for re in recommended:
                jugadores.append(Jugador.objects.get(pk=re[1]))
                similar.append(re[0])
            items= zip(jugadores,similar)
            return render(request,'jugadores_similares.html', {'jugador': jugador,'jugadores': items})
   


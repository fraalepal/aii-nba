#encoding:utf-8
from typing import Generic
from main.recommendations import calculateSimilarItems, getRecommendations, getRecommendedItems, topMatches, transformPrefs
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from main.forms import BusquedaPorEquipoWHForm, BusquedaPorNombreForm, BusquedaPorPosicionDraftForm, BusquedaPorPosicionForm, BusquedaPorPosicionJugadorWHForm, BusquedaPorPosicionWHForm, BusquedaPorTituloForm, EquipoForm, FilmForm
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

def loadDict(request):
    Prefs={}   # matriz de equipos y puntuaciones a cada a jugador
    shelf = shelve.open("dataRS.dat")
    jugadores = Jugador.objects.all()
    pos = Posicion.objects.all()
    for j in jugadores:
        user = j.id
        perFiltro = int(float(j.per))
        per = round(float(j.per),2)
        for p in pos:
            if p.posicionNombre==j.posicionJugador:
                posicion = p.posicionNombre
                idpos = p.id
        
                Prefs.setdefault(user, {})   
                #Prefs[user][idpos] = idpos
                Prefs[user][perFiltro] = per
                
                print(Prefs)
        
    shelf['Prefs']=Prefs
    #shelf['ItemsPrefs']=transformPrefs(Prefs)
    #shelf['SimItems']=calculateSimilarItems(Prefs, n=4)
    shelf.close()
    return render(request,'loadRS.html')


def loadRS():
    loadDict()
    
#Aqui anda
def similarPlayers(request):
    film = None
    if request.method=='GET':
        form = FilmForm(request.GET, request.FILES)
        if form.is_valid():
            idFilm = form.cleaned_data['id']
            film = get_object_or_404(Jugador, pk=idFilm)
            shelf = shelve.open("dataRS.dat")
            ItemsPrefs = shelf['Prefs']
            shelf.close()
            idJugador = film.id
            recommended = topMatches(ItemsPrefs, int(idJugador),n=3)
            films = []
            similar = []
            for re in recommended:
                films.append(Jugador.objects.get(pk=re[1]))
                similar.append(re[0])
            items= zip(films,similar)
            return render(request,'similarFilms.html', {'film': film,'films': items})
    form = FilmForm()
    return render(request,'search_film.html', {'form': form})

def recommendedPlayerItems(request):
    if request.method=='GET':
        form = EquipoForm(request.GET, request.FILES)
        if form.is_valid():
            user = form.cleaned_data['equipo']
            shelf = shelve.open("dataRS.dat")
            Prefs = shelf['Prefs']
            SimItems = shelf['SimItems']
            shelf.close()
            try:
                rankings = getRecommendedItems(Prefs, SimItems, int(user))
                recommended = rankings[:3]
                animes = []
                scores = []
                for re in recommended:
                    animes.append(Jugador.objects.get(pk=re[1]))
                    scores.append(re[0])
                items= zip(animes,scores)
            except:
                items = []
            return render(request,'recommendationItems.html', {'user': user, 'items': items})
    form = EquipoForm()
    return render(request,'search_user.html', {'form': form})  
    

#Funciones para popular en Whoosh

def schemaNoticias():
    schema = Schema(imagenNoticia=TEXT(stored=True),
                    titulo=TEXT(stored=True),
                    enlace=TEXT(stored=True),
                    contenido=TEXT(stored=True))
    return schema

def schemaDrafteado():
    schema = Schema(nombreJugador=TEXT(stored=True),
                    posicionJugador=TEXT(stored=True),
                    universidad=TEXT(stored=True),
                    pickJugador=NUMERIC(stored=True))
    return schema

def schemaPosicionDraft():
    schema = Schema(posicionNombre=TEXT(stored=True))
    return schema

def schemaJugador():
    schema = Schema(imagenJugador=TEXT(stored=True),
                    nombreJugador=TEXT(stored=True),
                    posicionJugador=TEXT(stored=True),
                    nombreEquipo=TEXT(stored=True),
                    salarioNumero=NUMERIC(stored=True),
                    puntosPorPartido=NUMERIC(stored=True, sortable=True),
                    asistenciasPorPartido=NUMERIC(stored=True),
                    rebotesPorPartido=NUMERIC(stored=True),
                    per=NUMERIC(stored=True),
                    id=NUMERIC(stored=True))
    return schema

def getNoticiaByTitulo(titulo):
    main_directory = 'main_info'
    news_directory = main_directory + '/' + 'news'
    ix = open_dir(news_directory)
    with ix.searcher() as searcher:
        entry = str(titulo)
        query = QueryParser('titulo', ix.schema).parse(entry)
        results = searcher.search(query)
        row = results[0]
        id = row['contenido']
    return id

#funciones auxiliares que hacen scraping en la web y carga los datos en la base datos 
def populateDB():
    #variables para contar el número de registros que vamos a almacenar
    num_equipos = 0

    Equipo.objects.all().delete()

    f = urllib.request.urlopen("https://espndeportes.espn.com/basquetbol/nba/equipos")
    s = BeautifulSoup(f, "lxml")
    columnas = s.find("div", class_=["layout__column", "layout__column--1"]).find_all("div", class_="layout__column")
    
    nombreEquipo = None
    ranking = None
    proxPartido = None
    estadisticas = []
    resultadoEst = []
    lesionados = []
    resultadoLesionados = []
    sumaSalarios = 0
    resultadoSuma = 0
    listaJugadores = []
    resultadoListaJugadores = []
    #Jugadores
    nombreJugador = None
    salarioNumero = None
    nombreEquipo = None
    logoEquipo = None 
    for columna in columnas:
        filas = columna.find_all("div", class_="mt7")
        for fila in filas:
            equipos = fila.find_all("div",class_="mt3")
            for equipo in equipos:
                nombreEquipo = equipo.find("div",class_="pl3").a.text
                enlace_portada_equipo = equipo.find("div",class_="pl3").a['href']
                enlace_portada = "https://espndeportes.espn.com"+enlace_portada_equipo
                lista_enlace_portada_equipo = []
                lista_enlace_portada_equipo.append(enlace_portada)

                try:
                    for link in lista_enlace_portada_equipo:
                        f = urllib.request.urlopen(link)
                        s = BeautifulSoup(f, "lxml")
                        try:
                            logoEquipo = s.find("div", class_="Image__Wrapper").picture.source['data-srcset']
                            ranking = s.find("div","ClubhouseHeader__TeamDetails").find("ul", class_="ClubhouseHeader__Record").find("li").find_next_sibling("li").text
                        
                            tablaHorario = s.find("section", class_="club-schedule").find("ul").find("li").find("a")
                        except:
                            ranking = "No existe registros"
                            tablaHorario = "No existe registro de próximo partido"

                        versus = tablaHorario.find("div", class_="game-info").string
                        fecha = tablaHorario.find("div", class_="game-meta").find("div", class_="game-date").span.text
                        hora = tablaHorario.find("div", class_="game-meta").find("div", class_="time").string
                        proxPartido = versus +  " " + fecha + " "+ hora

                        stats = s.find("article", class_="rankings").find("div", class_="content").find_all("div", class_="grid-rank")
                        for elemento in stats:
                            
                            nombreStat = elemento.span.text
                            numberStat = elemento.find("span").find_next_sibling("span").text
                            diccionario = {nombreStat,numberStat}
                            estadisticas.append(diccionario)
                        resultadoEst = estadisticas
                        estadisticas = []
                        #BLOQUE TRY CARCH QUE COMPRUEBE LA EXISTENCIA DE LESIONADOS
                        
                        for link in lista_enlace_portada_equipo:
                            f = urllib.request.urlopen(link)
                            s = BeautifulSoup(f, "lxml")
                            
                            try:
                                lesiones = s.find("section", class_="col-c").find("article").find_next_sibling("article").find_next_sibling("article").find("div", class_="content").find("ul").find_all("li")
                                for elemento in lesiones:
                                    nombrelesionado = elemento.find("div", class_="content-meta").h2.a.text 
                                    lesionados.append(nombrelesionado)     
                                resultadoLesionados = lesionados
                                lesionados = []
                            except:
                                resultadoLesionados = "No existen registro de lesionados"
                                 
                        
                except:
                    record = "No existe registros"
                    proxPartido = "No existe registros"
                    ranking = "No existe registros"
                    lista_enlace_plantilla = enlace_portada_equipo.split("equipo/")
                    enlace_estadisticas = "https://espndeportes.espn.com/basquetbol/nba/equipo/estadisticas/"+lista_enlace_plantilla[1]
                    lista_enlaces_estadisticas = []
                    lista_enlaces_estadisticas.append(enlace_estadisticas)
                    for link in lista_enlaces_estadisticas:
                        f = urllib.request.urlopen(link)
                        s = BeautifulSoup(f, "lxml")

                        headTabla = s.find("div", class_="Table__Scroller").find("table").find("thead", class_="Table__THEAD").find_all("th")
                        tabla = s.find("div", class_="Table__Scroller").find("table").find("tbody", class_="Table__TBODY").find_all("td", class_="Stats__TotalRow")
                        nombrePts = headTabla[3].span["title"]
                        nombreReb = headTabla[6].span["title"]
                        nombreAst = headTabla[7].span["title"]

                        numberPts = tabla[3].span.text
                        numberReb = tabla[6].span.text
                        numberAst = tabla[7].span.text

                        diccionariopts = {nombrePts,numberPts}
                        diccionarioreb = {nombreReb,numberReb}
                        diccionarioast = {nombreAst,numberAst}

                        estadisticas.append(diccionariopts)
                        estadisticas.append(diccionarioreb)
                        estadisticas.append(diccionarioast)
                    resultadoEst = estadisticas
                    estadisticas = []
                

                lista_enlace_plantilla = enlace_portada_equipo.split("equipo/")
                enlace_plantilla = "https://espndeportes.espn.com/basquetbol/nba/equipo/plantel/"+lista_enlace_plantilla[1]
                lista_enlaces = []
                lista_enlaces.append(enlace_plantilla)
                for link in lista_enlaces:
                    f = urllib.request.urlopen(link)
                    s = BeautifulSoup(f, "lxml")
                    
                    tabla = s.find("table").find("tbody", class_="Table__TBODY").find_all("tr")
                    for elemento in tabla:
                        celdaNombre = elemento.find("td").find_next_sibling("td")
                        nombreJugador = celdaNombre.a.text
                        celdaPosicion = celdaNombre.find_next_sibling("td")
                        posicionJugador = celdaPosicion.text
                        celdaEdad = celdaPosicion.find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td")
                        salario = celdaEdad.find_next_sibling("td").text
                        lista_salario = salario.split("$")
                        
                        if(salario == "--"):
                            salarioNumero = 0
                        else:
                            salarioNumero = int(lista_salario[1].replace(",",""))
                        sumaSalarios += salarioNumero                        
                        listaJugadores.append(nombreJugador)

                    resultadoSuma = sumaSalarios
                    resultadoListaJugadores = listaJugadores
                    listaJugadores = []
                    sumaSalarios = 0

                print(nombreEquipo)
                nombrerequipo_obj, creado = Equipo.objects.get_or_create(logoEquipo = logoEquipo, nombreEquipo = nombreEquipo, ranking = ranking, proxPartido = proxPartido, estadisticas =resultadoEst, lesionados = resultadoLesionados, listaJugadores = resultadoListaJugadores, sumaSalarios = resultadoSuma )
                    
                if creado:
                    num_equipos = num_equipos + 1

                '''try:
                    e = Equipo.objects.create(logoEquipo = logoEquipo, nombreEquipo = nombrerequipo_obj, ranking = ranking, proxPartido = proxPartido, estadisticas =resultadoEst, lesionados = resultadoLesionados, listaJugadores = resultadoListaJugadores, sumaSalarios = resultadoSuma )
                    print(nombreEquipo)
                except:
                    continue
                
                rows = Equipo.objects.all()
                for row in rows:
                    try:
                        Equipo.objects.get(nombreEquipo=row.nombreEquipo)
                    except:
                        row.delete()'''


    return ((num_equipos))

def populateJugadoresDB():

    main_directory = 'main_info'
    jugadores_directory = main_directory + '/' + 'jugadores'
    if not os.path.exists(main_directory):
        os.mkdir(main_directory)
    if not os.path.exists(jugadores_directory):
        os.mkdir(jugadores_directory)
    ix1 = create_in(jugadores_directory, schema=schemaJugador())
    writer1 = ix1.writer()

    count_jugadores = 1

    num_jugador = 0
    num_posiciones = 0
    Jugador.objects.all().delete()

    f = urllib.request.urlopen("https://espndeportes.espn.com/basquetbol/nba/equipos")
    s = BeautifulSoup(f, "lxml")
    columnas = s.find("div", class_=["layout__column", "layout__column--1"]).find_all("div", class_="layout__column")


    nombreJugador = None 
    nombreEquipo = None
    posicionJugador = None
    salarioNumero = None 
    resNombreJugador = None
    resPosicionJugador = None
    resSalarioNumero = None
    resNombreEquipo = None              
    for columna in columnas:
        filas = columna.find_all("div", class_="mt7")
        for fila in filas:
            equipos = fila.find_all("div",class_="mt3")
            for equipo in equipos:
                nombreEquipo = equipo.find("div",class_="pl3").a.text
                enlace_portada_equipo = equipo.find("div",class_="pl3").a['href']
                enlace_portada = "https://espndeportes.espn.com"+enlace_portada_equipo
                lista_enlace_portada_equipo = []
                lista_enlace_portada_equipo.append(enlace_portada)

                lista_enlace_plantilla = enlace_portada_equipo.split("equipo/")
                enlace_plantilla = "https://espndeportes.espn.com/basquetbol/nba/equipo/plantel/"+lista_enlace_plantilla[1]
                lista_enlaces = []
                lista_enlaces.append(enlace_plantilla)
                for link in lista_enlaces:
                    f = urllib.request.urlopen(link)
                    s = BeautifulSoup(f, "lxml")
                        
                    tabla = s.find("table").find("tbody", class_="Table__TBODY").find_all("tr")
                    for elemento in tabla:
                        imagen = elemento.find("td").img['alt']
                        celdaNombre = elemento.find("td").find_next_sibling("td")
                        nombreJugador = celdaNombre.a.text
                        linkJugador = celdaNombre.a['href']

                        celdaPosicion = celdaNombre.find_next_sibling("td")
                        posicionJugador = celdaPosicion.text

                        if posicionJugador=="A":
                            posicionJugador == "Pívot"

                        if posicionJugador=="G":
                            posicionJugador == "Base"

                        if posicionJugador == "C":
                            posicionJugador == "Pívot"

                        if posicionJugador == "SF":
                            posicionJugador =="Alero"
                        
                        if posicionJugador == "AP":
                            posicionJugador =="Ala Pívot"

                        posiciones = []
                        


                        celdaEdad = celdaPosicion.find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td")
                        salario = celdaEdad.find_next_sibling("td").text
                        lista_salario = salario.split("$")
                            
                        if(salario == "--"):
                            salarioNumero = 0
                        else:
                            salarioNumero = int(lista_salario[1].replace(",",""))

                        try: 
                            file = urllib.request.urlopen(linkJugador)
                            soup = BeautifulSoup(file, "lxml")
                            stats = soup.find("div", class_="PlayerHeader__Container").find("div", class_="PlayerHeader__Right").find("ul")
                            ppp = stats.find("li", class_="flex-expand").find("div", class_="StatBlockInner").find("div", class_="StatBlockInner__Value").text
                            app = stats.find("li", class_="flex-expand").find_next_sibling("li", class_="flex-expand").find("div", class_="StatBlockInner").find("div", class_="StatBlockInner__Value").text
                            rpp = stats.find("li", class_="flex-expand").find_next_sibling("li", class_="flex-expand").find_next_sibling("li", class_="flex-expand").find("div", class_="StatBlockInner").find("div", class_="StatBlockInner__Value").text
                            per = float(stats.find("li", class_="flex-expand").find_next_sibling("li", class_="flex-expand").find_next_sibling("li", class_="flex-expand").find_next_sibling("li", class_="flex-expand").find("div", class_="StatBlockInner").find("div", class_="StatBlockInner__Value").text)
                            if per < 0.0:
                                per = 0.0
                        except:
                            ppp = 0.0
                            app = 0.0
                            rpp = 0.0
                            per = 0.0
                            continue
                        
                        resImagenJugador = imagen
                        resNombreJugador = nombreJugador
                        resPosicionJugador = posicionJugador
                        if resPosicionJugador == "C":
                            resPosicionJugador = "Pívot"
                        elif resPosicionJugador == "BA":
                            resPosicionJugador = "Base"
                        elif resPosicionJugador == "E":
                            resPosicionJugador = "Escolta"
                        elif resPosicionJugador == "SF":
                            resPosicionJugador = "Alero"
                        elif resPosicionJugador == "AP":
                            resPosicionJugador = "Ala Pívot"

                        posiciones.append(resPosicionJugador)


                        resNombreEquipo = nombreEquipo
                        resSalarioNumero = salarioNumero
                        resPPP = float(ppp)
                        resAPP = float(app)
                        resRPP = float(rpp)
                        
                        #resPer = ((5*resPer)/35)

                        lista_posiciones_obj = []
                        for posicion in posiciones:
                            posicion_obj, creado = Posicion.objects.get_or_create(posicionNombre=posicion)
                            lista_posiciones_obj.append(posicion_obj)
                            if creado:
                                num_posiciones = num_posiciones + 1
                        

                        equipoKey = Equipo.objects.get(nombreEquipo=nombreEquipo)

                        
                        nombrejugador_obj, creado = Jugador.objects.get_or_create(imagenJugador = resImagenJugador, nombreJugador = nombreJugador, posicionJugador = resPosicionJugador, nombreEquipo = equipoKey, salarioNumero =resSalarioNumero, puntosPorPartido = resPPP, asistenciasPorPartido = resAPP, rebotesPorPartido = resRPP, per = per)
                        
                        if creado:
                            num_jugador = num_jugador + 1
                            print(nombreJugador+" con per ="+ str(per) )
                            print(str(num_jugador))

                        writer1.add_document(imagenJugador = resImagenJugador, nombreJugador = resNombreJugador, posicionJugador = resPosicionJugador, nombreEquipo = resNombreEquipo, salarioNumero =resSalarioNumero, puntosPorPartido = resPPP, asistenciasPorPartido = resAPP, rebotesPorPartido = resRPP, per = per, id = nombrejugador_obj.id)
                        # Se incrementa el id del jugador
                        count_jugadores = count_jugadores + 1

                        '''j = Jugador.objects.create(imagenJugador = resImagenJugador, nombreJugador = nombrejugador_obj, posicionJugador = resPosicionJugador, nombreEquipo = nombrerequipo_obj.nombreEquipo, salarioNumero =resSalarioNumero, puntosPorPartido = resPPP, asistenciasPorPartido = resAPP, rebotesPorPartido = resRPP)
                        print(nombreJugador)
                        rows = Jugador.objects.all()
                        for row in rows:
                            try:
                                Jugador.objects.get(nombreJugador=row.nombreJugador)
                            except:
                                row.delete()'''

    print('Se han indexado ' + str(count_jugadores-1) + ' jugadores')
    print('---------------------------------------------------------')
    writer1.commit()
    return ((num_jugador, count_jugadores-1))

def populateDrafteadosDB():

    main_directory = 'main_info'
    drafteados_directory = main_directory + '/' + 'drafteados'
    if not os.path.exists(main_directory):
        os.mkdir(main_directory)
    if not os.path.exists(drafteados_directory):
        os.mkdir(drafteados_directory)
    ix1 = create_in(drafteados_directory, schema=schemaDrafteado())
    writer1 = ix1.writer()

    count_drafteados = 1

    num_drafteados = 0
    num_posiciones = 0
    Drafteado.objects.all().delete()
    PosicionDraft.objects.all().delete()

    for i in range (1,5):
        ff = urllib.request.urlopen("https://espndeportes.espn.com/basquetbol/nba/draft/mejordisponible/_/posicion/ovr/pagina/"+str(i))
        ss = BeautifulSoup(ff, "lxml")
        tablaDraft = ss.find("div", class_=["draftTable","draftTable--bestavailable"]).find("div",class_="draftTable__tbody").find("ul").find_all("li")


        for drafteado in tablaDraft:
            pickJugador = drafteado.a.span.text
            nombreJugador = drafteado.find("div", class_="draftTable__playerInfo").find("span").text
            universidad = drafteado.find("div", class_="draftTable__playerInfo").find("span").find_next_sibling("span").text
            posicionJugador = drafteado.find("span", class_="draftTable__headline--pos").text

            print(posicionJugador)

            posiciones = []
            

            resNombreJugador = nombreJugador
            resPosicionJugador = posicionJugador
            if resPosicionJugador == "C":
                resPosicionJugador = "Pívot"
            elif resPosicionJugador == "PG":
                resPosicionJugador = "Base"
            elif resPosicionJugador == "SG":
                resPosicionJugador = "Escolta"
            elif resPosicionJugador == "SF":
                resPosicionJugador = "Alero"
            elif resPosicionJugador == "PF":
                resPosicionJugador = "Ala Pívot"
            resUniversidad = universidad
            resPickJugador = pickJugador

            posiciones.append(resPosicionJugador)

            lista_posiciones_obj = []
            for posicion in posiciones:
                posicion_obj, creado = PosicionDraft.objects.get_or_create(posicionNombre=posicion)
                lista_posiciones_obj.append(posicion_obj)
                if creado:
                    num_posiciones = num_posiciones + 1

            nombredrafteado_obj, creado = Drafteado.objects.get_or_create(nombreJugador=resNombreJugador)
            if creado:
                num_drafteados = num_drafteados + 1

            d = Drafteado.objects.create(pickJugador =resPickJugador, nombreJugador = nombredrafteado_obj, posicionJugador = resPosicionJugador, universidad = resUniversidad)
            
            writer1.add_document(pickJugador =resPickJugador, nombreJugador = resNombreJugador, posicionJugador = resPosicionJugador, universidad = resUniversidad)
            # Se incrementa el id del jugador
            count_drafteados = count_drafteados + 1
            
            rows = Drafteado.objects.all()
            for row in rows:
                try:
                    Drafteado.objects.get(nombreJugador=row.nombreJugador)
                except:
                    row.delete()

    print('Se han indexado ' + str(count_drafteados-1) + ' drafteados')
    print('---------------------------------------------------------')
    writer1.commit()
    return ((num_drafteados, count_drafteados-1))

def populateNoticiasDB():

    main_directory = 'main_info'
    news_directory = main_directory + '/' + 'news'
    if not os.path.exists(main_directory):
        os.mkdir(main_directory)
    if not os.path.exists(news_directory):
        os.mkdir(news_directory)
    ix1 = create_in(news_directory, schema=schemaNoticias())
    writer1 = ix1.writer()

    count_news = 1

    num_noticias = 0

    #Noticia.objects.all().delete()

    f = urllib.request.urlopen("https://www.marca.com/baloncesto/nba.html?intcmp=MENUMIGA&s_kw=noticias")
    s = BeautifulSoup(f, "lxml")
    noticias = s.find("div", class_=["fix-c", "content-items"]).find("ul", class_="auto-items").find_all("li", class_="content-item")

    imagenN = None
    tituloN = None 
    contenidoN = None 
    enlaceN = None
    imagenNoticia = None 
    fechaNoticia = None
    fecha = None
    for articulo in noticias:
        titulo = articulo.find("article").find("header", class_="mod-header").h3.a.text
        enlace = articulo.find("article").find("header", class_="mod-header").h3.a['href']
        lista_enlaces_noticias = []
        lista_enlaces_noticias.append(enlace)
        for link in lista_enlaces_noticias:
            ff = urllib.request.urlopen(link)
            ss = BeautifulSoup(ff, "lxml")
            try:
                imagenNoticia = ss.find("div", class_=["row","content"]).find_next_sibling("div", class_=["row","content"]).img['src']
                contenido = ss.find("div", class_=["row","content"]).find_next_sibling("div", class_=["row","content"]).find("p", class_=False).text
                
            except:
                contenido = "No existe"
                imagenNoticia ="https://www.gigantes.com/wp-content/uploads/2020/01/THUMBNAIL_077-3.jpg"

            imagenN = imagenNoticia
            tituloN= titulo
            enlaceN = enlace
            contenidoN = contenido
        
        writer1.add_document(imagenNoticia = imagenN, titulo=tituloN, enlace=enlaceN, contenido=contenidoN)
        # Se incrementa el id del jugador
        count_news = count_news + 1

        titulo_obj, creado = Noticia.objects.get_or_create(titulo=tituloN)
        if creado:
            num_noticias = num_noticias + 1
            print(titulo)

        n = Noticia.objects.create(imagenNoticia = imagenN, titulo =titulo_obj, enlace = enlaceN, contenido = contenidoN)
        rows = Noticia.objects.all()
        for row in rows:
            try:
                Noticia.objects.get(titulo=row.titulo)
            except:
                row.delete()

    print('Se han indexado ' + str(count_news-1) + ' noticias')
    print('---------------------------------------------------------')
    writer1.commit()
    return ((num_noticias, count_news)) 


#carga los datos desde la web en la BD
@login_required(login_url='/login')
def carga(request):

    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_equipos = populateDB()
            num_jugador = populateJugadoresDB()
            #num_drafteados = populateDrafteadosDB()
            #num_noticias = populateNoticiasDB()
            #mensaje="Se han almacenado: " + str(num_noticias) +" noticias, " 
            mensaje="Se han almacenado: " + str(num_jugador)+"  jugadores " + str(num_equipos)+ " equipos"
            #mensaje="Se han almacenado: " + str(num_equipos) +" equipos, " + str(num_jugador)+" jugadores, "+ str(num_drafteados)+"  posibles drafteados y "+str(num_noticias) +" noticias"
            es_admin = request.user.exists()
            return render(request, 'cargaBD.html', {'mensaje':mensaje , 'es_admin' : es_admin})
        else:
            return redirect("/")
           
    return render(request, 'confirmacion.html')

@login_required(login_url='/login')
def carga_nuevas_noticias(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_noticias = populateNoticiasDB()
            mensaje="Se han almacenado: " + str(num_noticias)  +" noticias"
            return redirect("/noticias")
        else:
            return redirect("/noticias")
           
    return render(request, 'confirmacion.html')

@login_required(login_url='/login')
def carga_nuevos_datos_equipos(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_equipos = populateDB()
            mensaje="Se han actualizado los datos de los: " + str(num_equipos)  +" equipos"
            return redirect("/equipos")
        else:
            return redirect("/equipos")
           
    return render(request, 'confirmacion.html')

@login_required(login_url='/login')
def carga_nuevos_datos_jugadores(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_jugadores = populateJugadoresDB()
            mensaje="Se han actualizado los datos de los: " + str(num_jugadores)  +" jugadores"
            return redirect("/jugadores")
        else:
            return redirect("/jugadores")
           
    return render(request, 'confirmacion.html')

@login_required(login_url='/login')
def carga_nuevos_datos_drafteados(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_drafteados = populateDrafteadosDB()
            mensaje="Se han actualizado los datos de los: " + str(num_drafteados)  +" drafteados"
            return redirect("/drafteados")
        else:
            return redirect("/drafteados")
           
    return render(request, 'confirmacion.html')

#muestra el número de películas que hay en la BD
def inicio(request):
    num_equipos=Equipo.objects.all().count()
    return render(request,'inicio.html', {'num_equipos':num_equipos})


##################################
def lista_equipos(request):
    equipos=Equipo.objects.all()
    return render(request,'equipos.html', {'equipos':equipos})

def lista_equipostest(request):
    equipostest=Equipo.objects.all()
    return render(request,'equipostest.html', {'equipostest':equipostest})

def lista_jugador(request):
    jugadores_list=Jugador.objects.all()
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
    noticias=Noticia.objects.all()
    return render(request,'noticias.html', {'noticias':noticias})

#######################################BUSQUEDAS

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



#######################################BUSQUEDAS WHOOSH

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

def buscar_noticias_titulo_equipo(request):
    formulario = BusquedaPorTituloForm(request.POST)
    formularioequipo = BusquedaPorEquipoWHForm(request.POST)
    noticias = None 
    if formulario.is_valid() and formularioequipo.is_valid():
        ix = open_dir("main_info/news")
        with ix.searcher() as searcher:
            titulo = formulario.cleaned_data['titulo']
            equipo = formularioequipo.cleaned_data['equipo']
            query = MultifieldParser(["titulo","contenido"], ix.schema).parse(str(titulo), str(equipo))
            noticias = []
            result = searcher.search(query, limit = 10)
            for r in result:
                aux = {"imagenNoticia" : r['imagenNoticia'], "titulo": r['titulo'], "enlace": r['enlace'], "contenido": r['contenido']}
                noticias.append(aux)
            print(noticias)

    return render(request, 'buscarnoticiasportituloyequipo.html', {'formulario': formulario, 'formularioequipo' : formularioequipo , 'noticias': noticias})


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

def buscar_jugadoresporposicion(request):
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

###############################################################################################################################################################################################
'''def login(request):
    # Creamos el formulario de autenticación vacío
    form = AuthenticationForm()
    if request.method == "POST":
        # Añadimos los datos recibidos al formulario
        form = AuthenticationForm(data=request.POST)
        # Si el formulario es válido...
        if form.is_valid():
            # Recuperamos las credenciales validadas
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Verificamos las credenciales del usuario
            user = authenticate(username=username, password=password)

            # Si existe un usuario con ese nombre y contraseña
            if user is not None:
                # Hacemos el login manualmente
                do_login(request, user)
                # Y le redireccionamos a la portada
                return redirect('/')

    return render(request, 'ingresar_django.html', {'formulario': form})'''

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

def logout(request):
    # Finalizamos la sesión
    do_logout(request)
    # Redireccionamos a la portada
    return redirect('/')

def buscar_jugadores_lideres_por_posicion(request):
    formulario = BusquedaPorPosicionForm()
    jugador = None
    
    if request.method=='POST':
        formulario = BusquedaPorPosicionForm(request.POST)      
        if formulario.is_valid():
            jugador = Jugador.objects.filter(posicionJugador = Posicion.objects.get(pk=formulario.cleaned_data['posicion'])).order_by("-puntosPorPartido")[:5]
    
    return render(request, 'buscarjugadoreslideresporposicion.html', {'formulario': formulario, 'jugador': jugador})

def insertarNuevaPuntuacion(request):
    mensaje ="Se ha votado correctamente"
    if request.method == 'POST':
        formulario = request.POST
        
        
        valor = formulario['valor']
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
            puntuacionParaActualizar.rating = valor
            puntuacionParaActualizar.save()
    

    return render(request,'jugadores.html', {'mensaje': mensaje})
                        

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

    totalpuntuaciones = serialize('json', puntuaciones)

    return render(request,'mispuntuaciones.html', {'jugadores': jugadores, 'valores': valores, 'ratings': totalpuntuaciones})

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


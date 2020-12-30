#encoding:utf-8
from main.forms import BusquedaPorPosicionForm
from main.models import Equipo, Jugador, Drafteado, Noticia, Posicion
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
import urllib.request
import lxml
from datetime import datetime

import os
from whoosh import qparser
from whoosh.fields import DATETIME, TEXT, ID, NUMERIC, Schema
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser, QueryParser

#Funciones para popular en Whoosh
def getNoticias():
    main_directory = 'main_info'
    news_directory = main_directory + '/' + 'news'
    if not os.path.exists(main_directory):
        os.mkdir(main_directory)
    if not os.path.exists(news_directory):
        os.mkdir(news_directory)
    ix1 = create_in(news_directory, schema=schemaNoticias())
    writer1 = ix1.writer()
    
    count_news = 1
    #SCRAPING
    f = urllib.request.urlopen("https://www.marca.com/baloncesto/nba.html?intcmp=MENUMIGA&s_kw=noticias")
    s = BeautifulSoup(f, "lxml")
    noticias = s.find("div", class_=["fix-c", "content-items"]).find("ul", class_="auto-items").find_all("li", class_="content-item")


    imagenN = None
    tituloN = None 
    contenidoN = None 
    enlaceN = None
    imagenNoticia = None 
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

            imagenN = imagenNoticia
            tituloN= titulo
            enlaceN = enlace
            contenidoN = contenido

            # Se guarda el jugador
        writer1.add_document(imagenNoticia = imagenN, titulo=tituloN, enlace=enlaceN, contenido=contenidoN)
        # Se incrementa el id del jugador
        count_news = count_news + 1


    
    print('Se han indexado ' + str(count_news-1) + ' noticias')
    print('---------------------------------------------------------')
    writer1.commit()
    return ((count_news))


def schemaNoticias():
    schema = Schema(imagenNoticia=TEXT(stored=True),
                    titulo=TEXT(stored=True),
                    enlace=TEXT(stored=True),
                    contenido=TEXT(stored=True))
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


                nombrerequipo_obj, creado = Equipo.objects.get_or_create(nombreEquipo=nombreEquipo)
                if creado:
                    num_equipos = num_equipos + 1


                e = Equipo.objects.create(logoEquipo = logoEquipo, nombreEquipo = nombrerequipo_obj, ranking = ranking, proxPartido = proxPartido, estadisticas =resultadoEst, lesionados = resultadoLesionados, listaJugadores = resultadoListaJugadores, sumaSalarios = resultadoSuma )
                rows = Equipo.objects.all()
                for row in rows:
                    try:
                        Equipo.objects.get(nombreEquipo=row.nombreEquipo)
                    except:
                        row.delete()


    return ((num_equipos))

def populateJugadoresDB():
    num_jugador = 0

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
                            
                        except:
                            ppp = 0.0
                            app = 0.0
                            rpp = 0.0
                            continue
                        
                        resImagenJugador = imagen
                        resNombreJugador = nombreJugador
                        resPosicionJugador = posicionJugador
                        resNombreEquipo = nombreEquipo
                        resSalarioNumero = salarioNumero
                        resPPP = float(ppp)
                        resAPP = float(app)
                        resRPP = float(rpp)

                        nombrejugador_obj, creado = Jugador.objects.get_or_create(nombreJugador=resNombreJugador)
                        if creado:
                            num_jugador = num_jugador + 1

                        j = Jugador.objects.create(imagenJugador = resImagenJugador, nombreJugador = nombrejugador_obj, posicionJugador = resPosicionJugador, nombreEquipo = resNombreEquipo, salarioNumero =resSalarioNumero, puntosPorPartido = resPPP, asistenciasPorPartido = resAPP, rebotesPorPartido = resRPP)
                        rows = Jugador.objects.all()
                        for row in rows:
                            try:
                                Jugador.objects.get(nombreJugador=row.nombreJugador)
                            except:
                                row.delete()


    return ((num_jugador))

def populateDrafteadosDB():

    num_drafteados = 0
    num_posiciones = 0
    Drafteado.objects.all().delete()

    for i in range (1,5):
        ff = urllib.request.urlopen("https://espndeportes.espn.com/basquetbol/nba/draft/mejordisponible/_/posicion/ovr/pagina/"+str(i))
        ss = BeautifulSoup(ff, "lxml")
        tablaDraft = ss.find("div", class_=["draftTable","draftTable--bestavailable"]).find("div",class_="draftTable__tbody").find("ul").find_all("li")


        for drafteado in tablaDraft:
            pickJugador = drafteado.a.span.text
            nombreJugador = drafteado.find("div", class_="draftTable__playerInfo").find("span").text
            universidad = drafteado.find("div", class_="draftTable__playerInfo").find("span").find_next_sibling("span").text
            posicionJugador = drafteado.find("span", class_="draftTable__headline--pos").text

            posiciones = []
            posiciones.append(posicionJugador)

            resNombreJugador = nombreJugador
            resPosicionJugador = posicionJugador
            resUniversidad = universidad
            resPickJugador = pickJugador

            lista_posiciones_obj = []
            for posicion in posiciones:
                posicion_obj, creado = Posicion.objects.get_or_create(posicionNombre=posicion)
                lista_posiciones_obj.append(posicion_obj)
                if creado:
                    num_posiciones = num_posiciones + 1

            nombredrafteado_obj, creado = Jugador.objects.get_or_create(nombreJugador=resNombreJugador)
            if creado:
                num_drafteados = num_drafteados + 1

            d = Drafteado.objects.create(pickJugador =resPickJugador, nombreJugador = nombredrafteado_obj, posicionJugador = resPosicionJugador, universidad = resUniversidad)

            
            rows = Drafteado.objects.all()
            for row in rows:
                try:
                    Drafteado.objects.get(nombreJugador=row.nombreJugador)
                except:
                    row.delete()

    return ((num_drafteados))

def populateNoticiasDB():

    num_noticias = 0

    Noticia.objects.all().delete()

    f = urllib.request.urlopen("https://www.marca.com/baloncesto/nba.html?intcmp=MENUMIGA&s_kw=noticias")
    s = BeautifulSoup(f, "lxml")
    noticias = s.find("div", class_=["fix-c", "content-items"]).find("ul", class_="auto-items").find_all("li", class_="content-item")

    imagenN = None
    tituloN = None 
    contenidoN = None 
    enlaceN = None
    imagenNoticia = None 
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

            imagenN = imagenNoticia
            tituloN= titulo
            enlaceN = enlace
            contenidoN = contenido

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

    return ((num_noticias)) 

#carga los datos desde la web haciendo uso de Whoosh
def cargaWH(request):

    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_noticias = getNoticias()
            mensaje="Se han indexado: " + str(num_noticias) +" noticias, " 
            return render(request, 'cargaWH.html', {'mensaje':mensaje})
        else:
            return redirect("/")
           
    return render(request, 'confirmacion.html')
#carga los datos desde la web en la BD
def carga(request):

    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            #num_equipos = populateDB()
            #num_jugador = populateJugadoresDB()
            #num_drafteados = populateDrafteadosDB()
            num_noticias = populateNoticiasDB()
            mensaje="Se han almacenado: " + str(num_noticias) +" noticias, " 

           # mensaje="Se han almacenado: " + str(num_equipos) +" equipos, " + str(num_jugador)+" jugadores, "+ str(num_drafteados)+"  posibles drafteados y "+str(num_noticias) +" noticias"
            return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            return redirect("/")
           
    return render(request, 'confirmacion.html')

def carga_nuevas_noticias(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_noticias = populateNoticiasDB()
            mensaje="Se han almacenado: " + str(num_noticias)  +" noticias"
            return redirect("/noticias")
        else:
            return redirect("/noticias")
           
    return render(request, 'confirmacion.html')

def carga_nuevos_datos_equipos(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_equipos = populateDB()
            mensaje="Se han actualizado los datos de los: " + str(num_equipos)  +" equipos"
            return redirect("/equipos")
        else:
            return redirect("/equipos")
           
    return render(request, 'confirmacion.html')

def carga_nuevos_datos_jugadores(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_jugadores = populateJugadoresDB()
            mensaje="Se han actualizado los datos de los: " + str(num_jugadores)  +" jugadores"
            return redirect("/jugadores")
        else:
            return redirect("/jugadores")
           
    return render(request, 'confirmacion.html')

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
    jugadores=Jugador.objects.all()
    return render(request,'jugadores.html', {'jugadores':jugadores})

def lista_drafteados(request):
    drafteados=Drafteado.objects.all()
    return render(request,'drafteados.html', {'drafteados':drafteados})

def lista_noticias(request):
    noticias=Noticia.objects.all()
    return render(request,'noticias.html', {'noticias':noticias})

#######################################BUSQUEDAS

def buscar_jugadoresporposicion(request):
    formulario = BusquedaPorPosicionForm()
    jugadores = None
    
    if request.method=='POST':
        formulario = BusquedaPorPosicionForm(request.POST)      
        if formulario.is_valid():
            jugadores = Drafteado.objects.filter(posicionJugador = Posicion.objects.get(pk=formulario.cleaned_data['posicion']))

    return render(request, 'buscardrafteadosporposicion.html', {'formulario':formulario, 'jugadoress':jugadores})
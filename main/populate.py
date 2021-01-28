#encoding:utf-8
import shelve
from main.models import Equipo, Jugador, Drafteado, Noticia, Posicion, PosicionDraft
from django.shortcuts import get_object_or_404, render, redirect
from bs4 import BeautifulSoup
import urllib.request
from django.contrib.auth.decorators import login_required

import os
from whoosh import qparser
from whoosh.fields import DATETIME, TEXT, ID, NUMERIC, Schema
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser, QueryParser

from django.db.models import Q



#Funciones de populación del sistema de recomedación
def loadDict(request):
    Prefs={}   # matriz de equipos y puntuaciones a cada a jugador
    shelf = shelve.open("dataRS.dat")
    jugadores = Jugador.objects.all()
    for j in jugadores:
        user = j.id
        perFiltro = int(float(j.per))
        per = round(float(j.per),2)
        Prefs.setdefault(user, {})   
        Prefs[user][perFiltro] = per
        print(Prefs)
        
    shelf['Prefs']=Prefs
    shelf.close()
    return render(request,'loadRS.html')

def loadRS():
    loadDict()
    


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




#funciones auxiliares que hacen scraping en la web y carga los datos en la base datos e indexan los datos.
def populateEquiposDB():
    #variables para contar el número de registros que vamos a almacenar
    num_equipos = 0

    Jugador.objects.all().delete()
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
                                lesiones = s.find("section", class_="col-c").find("article").find_next_sibling("article").find_next_sibling("article").find_next_sibling("article").find("div", class_="content").find("ul").find_all("li")
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

                
                
                rows = Equipo.objects.all()
                for row in rows:
                    try:
                        Equipo.objects.get(nombreEquipo=row.nombreEquipo)
                    except:
                        row.delete()


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
                        elif resPosicionJugador == "A":
                            resPosicionJugador = "Ala Pívot"
                        elif resPosicionJugador == "G":
                            resPosicionJugador = "Escolta"

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


#carga los datos desde la web a la BD e indices de Whoosh
@login_required(login_url='/login')
def carga(request):

    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_equipos = populateEquiposDB()
            num_jugador = populateJugadoresDB()
            num_drafteados = populateDrafteadosDB()
            num_noticias = populateNoticiasDB()
            mensaje="Se han almacenado: " + str(num_equipos) +" equipos, " + str(num_jugador)+" jugadores, "+ str(num_drafteados)+"  posibles drafteados y "+str(num_noticias) +" noticias"
            return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            return redirect("/")
           
    return render(request, 'confirmacion.html')

#Función de carga individual de noticias
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

#Función de carga individual de equipos
@login_required(login_url='/login')
def carga_nuevos_datos_equipos(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_equipos = populateEquiposDB()
            populateJugadoresDB()
            mensaje="Se han actualizado los datos de los: " + str(num_equipos)  +" equipos"
            return redirect("/equipos")
        else:
            return redirect("/equipos")
           
    return render(request, 'confirmacion.html')

#Función de carga individual de jugadores
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

#Función de carga individual de drafteados
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



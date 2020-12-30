#encoding:utf-8
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml
from datetime import datetime 
 
'''
f = urllib.request.urlopen("https://espndeportes.espn.com/basquetbol/nba/equipo/plantel/_/nombre/bos/boston-celtics")
s = BeautifulSoup(f, "lxml")
lista_jugadores = []
record = s.find("div","ClubhouseHeader__TeamDetails").find("ul", class_="ClubhouseHeader__Record").find("li").find_next_sibling("li").text
print(record)


tabla = s.find("table").find("tbody", class_="Table__TBODY").find_all("tr")

for elemento in tabla:

    nombreJugador = elemento.find("td").find_next_sibling("td").a.text
    print(nombreJugador)




f = urllib.request.urlopen("https://espndeportes.espn.com/basquetbol/nba/equipo/_/nombre/bos/boston-celtics")
s = BeautifulSoup(f, "lxml")
estadisticas = []
stats = s.find("article", class_="rankings").find("div", class_="content").find_all("div", class_="grid-rank")
for elemento in stats:
    nombreStat = elemento.span.text
    numberStat = elemento.find("span").find_next_sibling("span").text
    diccionario = {nombreStat,numberStat}
'''

'''
f = urllib.request.urlopen("https://espndeportes.espn.com/basquetbol/nba/equipo/_/nombre/bos/boston-celtics")
s = BeautifulSoup(f, "lxml")
lesiones = s.find("section", class_="col-c").find("article").find_next_sibling("article").find_next_sibling("article").find("div", class_="content").find("ul").find_all("li")
for elemento in lesiones:
    nombrelesionado = elemento.find("div", class_="content-meta").h2.a.text 
    print(nombrelesionado)

'''



'''
enlace_estadisticas = "https://espndeportes.espn.com/basquetbol/nba/equipo/estadisticas/_/nombre/chi/chicago-bulls"
f = urllib.request.urlopen(enlace_estadisticas)
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




print(nombreReb)
'''
'''
f = urllib.request.urlopen("https://espndeportes.espn.com/basquetbol/nba/equipo/_/nombre/bos/boston-celtics")
s = BeautifulSoup(f, "lxml")

tablaHorario = s.find("section", class_="club-schedule").find("ul").find("li").find("a")
versus = tablaHorario.find("div", class_="game-info").string
fecha = tablaHorario.find("div", class_="game-meta").find("div", class_="game-date").span.text
hora = tablaHorario.find("div", class_="game-meta").find("div", class_="time").string
proxPartido = versus +  " " + fecha + " "+ hora
print(proxPartido)

#SCRAPPING INFO SOBRE DRAFT

for i in range (1,3):
    f = urllib.request.urlopen("https://espndeportes.espn.com/basquetbol/nba/draft/mejordisponible/_/posicion/ovr/pagina/"+str(i))
    s = BeautifulSoup(f, "lxml")
    tablaDraft = s.find("div", class_=["draftTable","draftTable--bestavailable"]).find("div",class_="draftTable__tbody").find("ul").find_all("li")


    for drafteado in tablaDraft:
        pick = drafteado.a.span.text
        nombre = drafteado.find("div", class_="draftTable__playerInfo").find("span").text
        universidad = drafteado.find("div", class_="draftTable__playerInfo").find("span").find_next_sibling("span").text
        position = drafteado.find("span", class_="draftTable__headline--pos").text
        print(pick+". "+nombre+" - "+universidad+" -")
        print(nombre)
        print(nombre)
        print(nombre)
f = urllib.request.urlopen("https://espndeportes.espn.com/basquetbol/nba/equipos")
s = BeautifulSoup(f, "lxml")
columnas = s.find("div", class_=["layout__column", "layout__column--1"]).find_all("div", class_="layout__column")

versus = None 
record = None 
proxPartido = None 
estadisticasString = None
estadisticas = []
lesionados = []
lista_jugadores = []
record = None
proxPartido = None
sumaSalarios = 0
nombreJugador = None 
posicionJugador = NONE
salarioNumero = None
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
                            record = s.find("div","ClubhouseHeader__TeamDetails").find("ul", class_="ClubhouseHeader__Record").find("li").find_next_sibling("li").text
                        
                            tablaHorario = s.find("section", class_="club-schedule").find("ul").find("li").find("a")
                        except:
                            record = "No existe registros"
                            tablaHorario = "No existe registro de próximo partido"

                        versus = tablaHorario.find("div", class_="game-info").string
                        fecha = tablaHorario.find("div", class_="game-meta").find("div", class_="game-date").span.text
                        hora = tablaHorario.find("div", class_="game-meta").find("div", class_="time").string
                        proxPartido = versus +  " " + fecha + " "+ hora

                        
                except:
                    record = "No existe registros"
                    proxPartido = "No existe registros"

                #BLOQUE TRY CARCH QUE COMPRUEBE LA EXISTENCIA DE PAGINA DE EQUIPO
                
                try:
                    for link in lista_enlace_portada_equipo:
                        f = urllib.request.urlopen(link)
                        s = BeautifulSoup(f, "lxml")
                        try:
                            record = s.find("div","ClubhouseHeader__TeamDetails").find("ul", class_="ClubhouseHeader__Record").find("li").find_next_sibling("li").text
                        
                            tablaHorario = s.find("section", class_="club-schedule").find("ul").find("li").find("a")
                        except:
                            record = "No existe registros"
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
                            estadisticasString = ''.join(str(e) for e in estadisticas)
                        print(estadisticasString)
                        #BLOQUE TRY CARCH QUE COMPRUEBE LA EXISTENCIA DE LESIONADOS
                        
                        
                        for link in lista_enlace_portada_equipo:
                            f = urllib.request.urlopen(link)
                            s = BeautifulSoup(f, "lxml")
                            
                            try:
                                lesiones = s.find("section", class_="col-c").find("article").find_next_sibling("article").find_next_sibling("article").find("div", class_="content").find("ul").find_all("li")
                                for elemento in lesiones:
                                    nombrelesionado = elemento.find("div", class_="content-meta").h2.a.text 
                                    lesionados.append(nombrelesionado)     
                            except:
                                noexiste = "No existen registro de lesionados"
                                lesionados.append(noexiste)
                except:
                    
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
                        estadisticasString = ''.join(str(e) for e in estadisticas)


                    noexiste = "No existen registro de lesionados"
                    lesionados.append(noexiste)
                print(lesionados)
                '''
'''
NOTICIAS NBA ESPN               
f = urllib.request.urlopen("https://espndeportes.espn.com/basquetbol/nba/equipos")
s = BeautifulSoup(f, "lxml")
columnas = s.find("div", class_=["layout__column", "layout__column--1"]).find_all("div", class_="layout__column")

contador = 0
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
                        seccion = s.find("section", class_="col-b").find_next_sibling("section", class_="col-b").find("div").find("div", class_="container-wrapper").find("div", class_="container").find_all("article", class_="news-feed-item")
                        for articulo in seccion:
                            titulo = articulo.find("div",class_="text-container").find("div", class_="item-info-wrap").h1.a.text
                            noticia = articulo.find("div",class_="text-container").find("div", class_="item-info-wrap").p.text
                            print(noticia)
                            print(" -------------------------------------")
                        contador += 1
                    print(contador)
                except:
                    record = "No existe registros"
                    proxPartido = "No existe registros"
'''
'''
f = urllib.request.urlopen("https://www.marca.com/baloncesto/nba.html?intcmp=MENUMIGA&s_kw=noticias")
s = BeautifulSoup(f, "lxml")
noticias = s.find("div", class_=["fix-c", "content-items"]).find("ul", class_="auto-items").find_all("li", class_="content-item")

titulo = None 
contenido = None 
enlace = None
for articulo in noticias:
    titulo = articulo.find("article").find("header", class_="mod-header").h3.a.text
    enlace = articulo.find("article").find("header", class_="mod-header").h3.a['href']
    lista_enlaces_noticias = []
    lista_enlaces_noticias.append(enlace)
    for link in lista_enlaces_noticias:
        ff = urllib.request.urlopen(link)
        ss = BeautifulSoup(ff, "lxml")
        try:
            enlace = link
            contenido = ss.find("div", class_=["row","content"]).find_next_sibling("div", class_=["row","content"]).find("p", class_=False).text
            print("Titulo:",titulo)
            print("Enlace:",link)
            print(contenido)
            print("------------------------------------------------")
        except:
            contenido = "No existe"
'''
'''
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
                    print(imagen)
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

                    
                    resNombreJugador = nombreJugador
                    resPosicionJugador = posicionJugador
                    resNombreEquipo = nombreEquipo
'''
'''
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
 
for columna in columnas:
    filas = columna.find_all("div", class_="mt7")
    for fila in filas:
        equipos = fila.find_all("div",class_="mt3")
        for equipo in equipos:
            logoEquipo = equipo.find("section", class_="TeamLinks").find("a").img['src']
            nombreEquipo = equipo.find("div",class_="pl3").a.text
            enlace_portada_equipo = equipo.find("div",class_="pl3").a['href']
            enlace_portada = "https://espndeportes.espn.com"+enlace_portada_equipo
            lista_enlace_portada_equipo = []
            lista_enlace_portada_equipo.append(enlace_portada)

            for link in lista_enlace_portada_equipo:
                ff = urllib.request.urlopen(link)
                ss = BeautifulSoup(ff, "lxml")
                logoEquipo = ss.find("div", class_="Image__Wrapper").picture.source['data-srcset']
                print(logoEquipo)
'''
f = urllib.request.urlopen("https://www.marca.com/baloncesto/nba.html?intcmp=MENUMIGA&s_kw=noticias")
s = BeautifulSoup(f, "lxml")
noticias = s.find("div", class_=["fix-c", "content-items"]).find("ul", class_="auto-items").find_all("li", class_="content-item")

tituloN = None 
contenidoN = None 
enlaceN = None
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
            print(imagenNoticia)
            contenido = ss.find("div", class_=["row","content"]).find_next_sibling("div", class_=["row","content"]).find("p", class_=False).text
        except:
            contenido = "No existe"

        tituloN= titulo
        enlaceN = enlace
        contenidoN = contenido
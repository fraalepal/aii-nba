#encoding:utf-8
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml
from datetime import datetime


#SCRAPING INFO SOBRE EQUIPOS
f = urllib.request.urlopen("https://espndeportes.espn.com/basquetbol/nba/equipos")
s = BeautifulSoup(f, "lxml")
columnas = s.find("div", class_=["layout__column", "layout__column--1"]).find_all("div", class_="layout__column")

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

            #BLOQUE TRY CARCH QUE COMPRUEBE LA EXISTENCIA DE PAGINA DE EQUIPO
            estadisticas = []
            lesionados = []
            lista_jugadores = []
            record = None
            proxPartido = None
            sumaSalarios = 0
            nombreJugador = None 
            posicionJugador = NONE
            salarioNumero = None
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


                noexiste = "No existen registro de lesionados"
                lesionados.append(noexiste)

            
                 
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
                    
                    print(nombreJugador+" - "+posicionJugador+" - "+str(salarioNumero)+" - "+nombreEquipo)
                    lista_jugadores.append(nombreJugador)

            '''        
            print(nombreEquipo)   
            print(lista_jugadores)
            print(estadisticas)
            print(lesionados)
            print(record)
            print(proxPartido)
            print(sumaSalarios)
            print("-----------------------")
            print(" ")
            '''
#AQUI HAY QUE AÑADIR LAS COSAS DE EQUIPOS Y JUGADORES A LA BBDD
            

#SCRAPING INFO SOBRE DRAFT
for i in range (1,5):
    ff = urllib.request.urlopen("https://espndeportes.espn.com/basquetbol/nba/draft/mejordisponible/_/posicion/ovr/pagina/"+str(i))
    ss = BeautifulSoup(ff, "lxml")
    tablaDraft = ss.find("div", class_=["draftTable","draftTable--bestavailable"]).find("div",class_="draftTable__tbody").find("ul").find_all("li")


    for drafteado in tablaDraft:
        pick = drafteado.a.span.text
        nombre = drafteado.find("div", class_="draftTable__playerInfo").find("span").text
        universidad = drafteado.find("div", class_="draftTable__playerInfo").find("span").find_next_sibling("span").text
        position = drafteado.find("span", class_="draftTable__headline--pos").text
        print(pick+". "+nombre+" - "+universidad+" - "+position)



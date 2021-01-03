from django.urls import path
from django.contrib import admin
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.inicio, name='inicio'),
    path('carga/',views.carga),
    path('carga_noticias/',views.carga_nuevas_noticias),
    path('carga_equipos/',views.carga_nuevos_datos_equipos),
    path('carga_jugadores/',views.carga_nuevos_datos_jugadores),
    path('carga_drafteados/',views.carga_nuevos_datos_drafteados),

    path('buscardrafteadosporposicion/', views.buscar_jugadoresporposicion),
    path('buscargleagueporposicion/', views.buscar_jugadoresgleagueporposicion),
    path('buscarnoticiasportitulo/', views.buscar_noticias_titulo),

    
    path('cargaWH/',views.cargaWH),

    path('equipos/', views.lista_equipos),
    path('equipostest/', views.lista_equipostest),
    path('jugadores/', views.lista_jugador),
    path('drafteados/', views.lista_drafteados),
    path('noticias/', views.lista_noticias),
    ]

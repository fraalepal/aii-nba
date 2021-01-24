from django.urls import path
from django.contrib import admin
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('logout/', views.logout),
    path('',views.inicio, name='inicio'),
    path('carga/',views.carga),
    path('carga_noticias/',views.carga_nuevas_noticias),
    path('carga_equipos/',views.carga_nuevos_datos_equipos),
    path('carga_jugadores/',views.carga_nuevos_datos_jugadores),
    path('carga_drafteados/',views.carga_nuevos_datos_drafteados),
    path('carga_RS/',views.loadDict),

    path('jugadoresRecomendadosEquipo/', views.recommendedPlayerItems),
    path('similarPlayers', views.similarPlayers),

    path('buscardrafteadosporposicion/', views.buscar_jugadoresporposicion),
    path('buscargleagueporposicion/', views.buscar_jugadoresgleagueporposicion),
    path('buscarnoticiasportitulo/', views.buscar_noticias_titulo),
    path('buscarnoticiasportituloyequipo/', views.buscar_noticias_titulo_equipo),

    path('buscarjugadorpornombre/', views.buscar_jugador_por_nombre),
    path('buscarjugadoreslideres/', views.buscar_jugadores_lideres_por_posicion),
    path('buscarjugadoresporequipo/', views.buscar_jugadores_por_equipo),
    
    path('equipos/', views.lista_equipos),
    path('equipostest/', views.lista_equipostest),
    path('jugadores/', views.lista_jugador),
    path('drafteados/', views.lista_drafteados),
    path('noticias/', views.lista_noticias),
    ]

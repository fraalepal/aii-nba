from django.urls import path
from django.contrib import admin
from main import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view()),
    path('signup/', views.SignUpView.as_view()),
    path('',views.inicio, name='inicio'),
    path('carga/',views.carga),
    path('carga_noticias/',views.carga_nuevas_noticias),
    path('carga_equipos/',views.carga_nuevos_datos_equipos),
    path('carga_jugadores/',views.carga_nuevos_datos_jugadores),
    path('carga_drafteados/',views.carga_nuevos_datos_drafteados),
    path('carga_RS/',views.loadDict),

    path('nuevapuntuacion/', views.insertarNuevaPuntuacion),
    path('mispuntuaciones/', views.misPuntuaciones),
    path('jugadoresRecomendadosPorUsuarios/', views.jugadoresRecomendadorPorUsuarios),

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

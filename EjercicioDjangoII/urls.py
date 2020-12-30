from django.urls import path
from django.contrib import admin
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.inicio, name='inicio'),
    path('carga/',views.carga),
    path('carga_noticias/',views.carga_nuevas_noticias),
    path('cargaWH/',views.cargaWH),
    path('equipos/', views.lista_equipos),
    path('equipostest/', views.lista_equipostest),
    path('jugadores/', views.lista_jugador),
    path('drafteados/', views.lista_drafteados),
    path('noticias/', views.lista_noticias),
    ]

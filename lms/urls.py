from django.urls import path, include
from . import views

# App URL patterns (site pages). The API router is mounted at project-level
urlpatterns = [
    path('', views.index, name='home'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
]

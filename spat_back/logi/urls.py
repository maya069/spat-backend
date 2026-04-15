from django.urls import path
from . import views

urlpatterns = [
    path('stock/',      views.stock,            name='logi-stock'),
    path('alertes/',    views.alertes,           name='logi-alertes'),
    path('mouvement/',  views.mouvement,         name='logi-mouvement'),
    path('mouvements/', views.mouvements_liste,  name='logi-mouvements'),
    path('chat/', views.logi_chat, name='logi-chat'),
    path('creer-et-mouvement/', views.creer_et_mouvement, name='creer-et-mouvement'),
]
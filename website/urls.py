from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.processar_video, name='processar_video'),
    path('download/', views.iniciar_download, name='iniciar_download'),
]

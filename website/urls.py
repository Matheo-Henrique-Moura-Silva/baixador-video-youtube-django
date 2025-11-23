from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.processar_download, name='processar_download'),
]

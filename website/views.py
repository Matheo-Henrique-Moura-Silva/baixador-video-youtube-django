from django.shortcuts import render, redirect, HttpResponse
from pytube import YouTube as MeuTube
from django.contrib import messages
from pytube.exceptions import VideoUnavailable, RegexMatchError, AgeRestrictedError

def index(request):
    if request.method == "GET":
        return render(request, 'index.html')

def processar_download(request):
    if request.method == "POST":
        video_url = request.POST.get("video_url")
        if not video_url:
            messages.warning(request, "URL vazia, tente novamente!")
            return redirect('website:index')
        else:
            messages.success(request, "URL OK!")
            return redirect('website:index')
    else:
        messages.info(request, "Cole a URL do video na barra de busca.")
        return redirect("website:index")

from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
import yt_dlp as MeuTube
from yt_dlp.utils import DownloadError, ExtractorError, SameFileError
import os
import tempfile
from django.http import FileResponse
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

DOWNLOAD_DIR = tempfile.gettempdir()

def index(request):
    if request.method == "GET":
        return render(request, 'index.html', {'mostrar_opcoes': False})

def iniciar_download(request):
    if request.method != "POST":
        messages.info(request, "Ação não permitida pelo sistema.")
        return redirect("website:index")

    url = request.POST.get("id_url")
    id = request.POST.get("id_formato")
    id_composto = f'{id}+bestaudio'

    FFMPEG_EXECUTABLE_PATH = r'C:\Program Files\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe'

    ydl_opts = {
        'format': id_composto,
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'cachedir': False,
        'nocheckcertificate': True,
        'ffmpeg_location': FFMPEG_EXECUTABLE_PATH,
    }

    downloaded_filepath = None
    file_to_serve = None

    try:
        with MeuTube.YoutubeDL(ydl_opts) as ydl:

            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', 'video_desconhecido')
            extensao = info_dict.get('ext', 'mp4')

            ydl.download([url])

            downloaded_filepath = ydl.prepare_filename(info_dict)
            file_to_serve = open(downloaded_filepath, 'rb')

            response = FileResponse(
                file_to_serve,
                as_attachment=True,
                filename=f"{video_title}.{extensao}"
            )

        def cleanup_file():
            print(f"Limpando arquivo: {downloaded_filepath}")

            if file_to_serve:
                file_to_serve.close()

            if os.path.exists(downloaded_filepath):
                try:
                    os.remove(downloaded_filepath)
                except PermissionError:
                    print(f"AVISO: Falha na exclusão do arquivo temporário.")

        response.closing_callback = cleanup_file
        return response

    except Exception as e:
        if file_to_serve:
            file_to_serve.close()

        messages.error(request, 'Ocorreu um erro interno ao iniciar o download.')
        return redirect('website:index')

def processar_video(request):
    if request.method != "POST":
        messages.info(request, "Cole a URL do video na barra de busca.")
        return redirect("website:index")

    video_url_bruto = request.POST.get("video_url")
    video_url = limpar_url_youtube(video_url_bruto)
    if not video_url:
        messages.warning(request, "URL vazia, tente novamente!")
        return redirect('website:index')

    video_opts = {
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        'force_generic_extractor': True,
        'socket_timeout': 15,
        'force_ipv4': True,
        'retries': 2,
        'cachedir': False,
    }
    try:
        with MeuTube.YoutubeDL(video_opts) as video_objeto:
            info_video = video_objeto.extract_info(video_url, download=False)

        if info_video is None or info_video.get('title') is None:
            raise ExtractorError('O extrator do MeuTube não conseguiu obter o título do vídeo.')

        titulo = info_video.get('title')
        thumbnail = info_video.get('thumbnail')

        formatos_brutos = info_video.get('formats')
        formatos_selecionados = filtrar_e_selecionar_qualidades(formatos_brutos)

        context = {
            'titulo': titulo,
            'thumbnail': thumbnail,
            'formatos': formatos_selecionados,
            'url': video_url,
            'mostrar_opcoes': True if formatos_selecionados else False,
        }

        return render(request, 'index.html', context)

    except (DownloadError):
        messages.error(request, 'URL inválida, verifique se o link está correto!')
        return redirect('website:index')

    except (ExtractorError):
        messages.error(request, 'MeuTube falhou ao analisar o vídeo (Tempo Limite Excedido ou Restrição)')
        return redirect('website:index')

    except Exception as e:
        messages.error(request, 'MeuTube falhou ao processar o vídeo.')
        return redirect('website:index')

def filtrar_e_selecionar_qualidades(formats):
    resolucoes_alvo = {
        144: None, 240: None, 360: None, 480: None, 720: None, 1080: None
    }

    if not formats:
        return None

    for f in formats:
        resolucao = f.get('height')
        ext = f.get('ext')
        filesize = f.get('filesize')
        tamanho = converter_para_megabytes(filesize)

        if not resolucao or ext not in ('mp4', 'webm') or not filesize:
            continue

        target_res = None
        if resolucao in resolucoes_alvo:
            target_res = resolucao

        if target_res:
            is_progressive = f.get('acodec') != 'none' and f.get('acodec') is not None

            if resolucoes_alvo[target_res] is None or \
                    (is_progressive and not resolucoes_alvo[target_res]['progressive']) or \
                    (filesize > resolucoes_alvo[target_res]['filesize']):

                if not is_progressive:
                    descricao = f"{target_res}p (Apenas Vídeo)"
                else:
                    descricao = f"{target_res}p ({ext})"

                resolucoes_alvo[target_res] = {
                    'format_id': f.get('format_id'),
                    'filesize': filesize,
                    'extensao': ext,
                    'descricao': descricao,
                    'progressive': is_progressive,
                    'tamanho': tamanho,
                }

    resultado_final = {k: v for k, v in resolucoes_alvo.items() if v is not None}
    if len(resultado_final) == 0:
        return None
    return resultado_final

def limpar_url_youtube(url_bruta):
    parsed_url = urlparse(url_bruta)
    query_params = parse_qs(parsed_url.query)
    if 'v' in query_params:
        video_id = query_params['v'][0]
        nova_query = urlencode({'v': video_id})
        url_limpa = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            '',
            nova_query,
            ''
        ))

        return url_limpa

    return url_bruta

def converter_para_megabytes(size_bytes):
    if size_bytes is None:
        return "Tamanho N/A"
    size_mb = size_bytes / (1024 * 1024)
    return f"{size_mb:.2f} MB"

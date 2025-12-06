document.addEventListener('DOMContentLoaded', function() {
    const formBuscar = document.getElementById('download-form');
    const spinnerBusca = document.getElementById('loading-spinner');
    const searchButton = document.getElementById('download-btn');
    const videoOptions = document.getElementById('video-options-section');
    const textVideoOptions = document.getElementById('text-video-options-section');
    const progressDownload = document.getElementById('loading-spinner-download');

    formBuscar.addEventListener('submit', function() {
        searchButton.disabled = true;
        searchButton.innerHTML = 'Aguarde<span id="spanc1" class="loading-dots">.</span><span id="spanc2" class="loading-dots">.</span><span id="spanc3" class="loading-dots">.</span>';
        spinnerBusca.classList.remove('spinner-hidden');
        videoOptions.classList.toggle('ocultar-section');
        textVideoOptions.classList.toggle('ocultar-section');
        progressDownload.classList.toggle('ocultar-section');
    });

    const downloadForms = document.querySelectorAll('.options-download');
    const sessionKeyInput = document.getElementById('session-key-hidden');
    const sessionKey = sessionKeyInput ? sessionKeyInput.value : null;
    const textOrientacao = document.getElementById('text-orientacao-site');
    
    downloadForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            
            const progressBarContainer = document.querySelector('#loading-spinner-download');
            const formatIdInput = form.querySelector('.id_formato');
            const formatId = formatIdInput ? formatIdInput.value : null;

            if (sessionKey && formatId) {
                const downloadKey = `${sessionKey}_${formatId}`;
                
                if (textOrientacao) {
                    textOrientacao.classList.add('ocultar-section');
                }
                progressBarContainer.classList.remove('spinner-hidden');

                setTimeout(() => {
                    startPolling(downloadKey);
                }, 100); 
                
            } else {
                console.error("Erro: Chave de Sessão ou ID de Formato ausente.");
            }
        });
    });
});

function startPolling(downloadKey) {
    const progressBar = document.getElementById('download-progress-bar');
    const progressText = document.getElementById('progress-text');
    const progressDownload = document.getElementById('loading-spinner-download');

    progressDownload.classList.remove('ocultar-section');
    
    progressBar.style.width = '0%';
    progressText.textContent = 'Iniciando Processamento...';
    
    const checkUrl = `/check-progress/?key=${downloadKey}`;
    
    const poll = setInterval(function() {
        fetch(checkUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Servidor respondeu com status ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                const percent = data.progress;

                if (percent < 0) { 
                    throw new Error('O download falhou devido a restrições.');
                }

                progressBar.style.width = percent + '%';
                progressText.textContent = `Download: ${percent.toFixed(2)}%`; 

                if (percent >= 100) {
                    clearInterval(poll);
                    const progressBar = document.getElementById('download-progress-bar');
                    if (progressBar) {
                        progressBar.classList.add('progress-finished');
                    }
                    progressText.textContent = 'Download Concluído!';
                }
            })
            .catch(error => {
                console.error('Erro no Polling:', error);
                clearInterval(poll);
                progressText.textContent = `Falha no Download: ${error.message}. Tente novamente.`;
                progressBar.style.width = '0%';
            });
    }, 1500);
}

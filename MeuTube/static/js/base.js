document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('download-form');
    const spinner = document.getElementById('loading-spinner');
    const searchButton = document.getElementById('download-btn');
    const videoOptions = document.getElementById('video-options-section');
    const textVideoOptions = document.getElementById('text-video-options-section');

    form.addEventListener('submit', function() {
        searchButton.disabled = true;
        searchButton.textContent = 'Aguarde...';
        spinner.classList.remove('spinner-hidden');
        videoOptions.classList.toggle('ocultar-section');
        textVideoOptions.classList.toggle('ocultar-section');
    });
});
export const UploadOverlay = {
    render(progress = 0, fileName = '') {
        if (progress === 0 && !fileName) return '';

        return `
      <div class="upload-progress-container glass">
        <div class="upload-header">
          <span class="upload-status">${progress < 100 ? 'Envoi en cours...' : 'Terminé'}</span>
          <button class="btn-close-mini" id="close-upload">×</button>
        </div>
        <div class="upload-file-info">
          <span class="file-name-mini">${fileName}</span>
          <span class="progress-percent">${progress}%</span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" style="width: ${progress}%"></div>
        </div>
      </div>
    `;
    },

    showDropZone() {
        const dz = document.getElementById('global-dropzone');
        if (dz) dz.classList.add('active');
    },

    hideDropZone() {
        const dz = document.getElementById('global-dropzone');
        if (dz) dz.classList.remove('active');
    }
};

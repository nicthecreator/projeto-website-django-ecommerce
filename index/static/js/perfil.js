document.addEventListener('DOMContentLoaded', () => {
    // Simula o clique para trocar o avatar
    const editAvatarBtn = document.querySelector('.edit-avatar-btn');
    if (editAvatarBtn) {
        editAvatarBtn.addEventListener('click', (e) => {
            e.preventDefault();
            alert('Funcionalidade de upload de imagem será implementada em breve!');
            // O código real criaria um <input type="file"> oculto e dispararia o click nele
        });
    }

    // Dá um destaque sutil na linha inteira quando o input é focado
    const inputs = document.querySelectorAll('.form-row input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            if (!this.classList.contains('readonly-input')) {
                this.parentElement.style.borderBottom = '1px solid #3b82f6';
            }
        });

        input.addEventListener('blur', function() {
            this.parentElement.style.borderBottom = '1px solid #f0f0f0';
        });
    });
});


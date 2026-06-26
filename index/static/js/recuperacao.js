document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('recoveryForm');

    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); 

            const email = document.getElementById('email').value;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const url = this.getAttribute('action');
            const btn = form.querySelector('.btn-entrar');

            // Feedback visual de carregamento
            btn.disabled = true;
            btn.innerText = 'Enviando...';
            btn.style.opacity = '0.7';

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ email: email })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                // Remove alertas antigos
                const alertaAntigo = document.getElementById('alerta-recuperacao');
                if (alertaAntigo) alertaAntigo.remove();

                const divAlerta = document.createElement('div');
                divAlerta.id = 'alerta-recuperacao';

                if (data.success) {
                    // Caixa Verde de Sucesso
                    divAlerta.style.cssText = "background-color: #dcfce7; color: #16a34a; padding: 12px; border-radius: 5px; margin-bottom: 20px; text-align: center; font-size: 14px; font-weight: 500;";
                    divAlerta.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${data.message}`;
                    form.reset(); // Limpa o campo de e-mail
                }

                // Insere a mensagem logo abaixo do parágrafo explicativo
                const paragrafo = document.querySelector('.login-box p');
                paragrafo.insertAdjacentElement('afterend', divAlerta);

                // Restaura o botão
                btn.disabled = false;
                btn.innerText = 'Enviar link de recuperação';
                btn.style.opacity = '1';
            })
            .catch(error => {
                const alertaAntigo = document.getElementById('alerta-recuperacao');
                if (alertaAntigo) alertaAntigo.remove();

                const divAlerta = document.createElement('div');
                divAlerta.id = 'alerta-recuperacao';
                // Caixa Vermelha de Erro
                divAlerta.style.cssText = "background-color: #fee2e2; color: #dc2626; padding: 12px; border-radius: 5px; margin-bottom: 20px; text-align: center; font-size: 14px;";
                divAlerta.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> ${error.message || 'Erro ao tentar recuperar a senha.'}`;
                
                const paragrafo = document.querySelector('.login-box p');
                paragrafo.insertAdjacentElement('afterend', divAlerta);

                btn.disabled = false;
                btn.innerText = 'Enviar link de recuperação';
                btn.style.opacity = '1';
            });
        });
    }
});
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('verificarForm');
    const inputCodigo = document.getElementById('codigo');
    const btnReenviar = document.getElementById('btnReenviar');

    // Função centralizada para exibir erros no ecrã
    function exibirErroCustomizado(mensagem) {
        const erroAntigo = document.getElementById('erro-codigo-box');
        if (erroAntigo) erroAntigo.remove();

        const divErro = document.createElement('div');
        divErro.id = 'erro-codigo-box';
        divErro.style.cssText = "background-color: #fee2e2; color: #dc2626; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; font-size: 14px; width: 100%; box-sizing: border-box;";
        divErro.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> ${mensagem}`;

        const h1 = document.querySelector('.login-box h1');
        if (h1) {
            h1.insertAdjacentElement('afterend', divErro);
        }
    }

    // Impede a digitação de letras
    if (inputCodigo) {
        inputCodigo.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    }

    // Validação principal e alteração do ecrã para a mensagem de sucesso
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); 

            const codigoDigitado = inputCodigo.value;
            
            if (codigoDigitado.length !== 6) {
                exibirErroCustomizado("O código deve conter exatamente 6 números.");
                return;
            }

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const url = this.getAttribute('action');

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ codigo: codigoDigitado })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Limpa mensagens de erro
                    const erroAntigo = document.getElementById('erro-codigo-box');
                    if (erroAntigo) erroAntigo.remove();

                    // Esconde o botão de reenvio
                    if (btnReenviar) btnReenviar.remove();

                    // Transforma o formulário na mensagem de sucesso
                    const loginBox = document.querySelector('.login-box');
                    if (loginBox) {
                        loginBox.innerHTML = `
                            <div style="text-align: center; padding: 10px 0;">
                                <h1 style="color: #16a34a; font-size: 26px; margin-bottom: 15px;">
                                    <i class="fa-solid fa-circle-check"></i> E-mail verificado!
                                </h1>
                                <p style="color: #444; font-size: 16px; margin-bottom: 25px; line-height: 1.5;">
                                    A sua conta foi ativada com sucesso.
                                </p>
                                <a href="${data.redirect_url || '/login/'}" class="btn-entrar" style="display: block; text-decoration: none; box-sizing: border-box;">
                                    Clique aqui para fazer login
                                </a>
                            </div>
                        `;
                    }
                }
            })
            .catch(error => {
                exibirErroCustomizado(error.message || "Código inválido ou expirado.");
            });
        });
    }

    // Lógica do botão de reenvio
    if (btnReenviar) {
        btnReenviar.addEventListener('click', function(e) {
            e.preventDefault();
            
            const urlReenviar = btnReenviar.getAttribute('data-url') || '/reenviar-codigo/';
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            btnReenviar.disabled = true;
            btnReenviar.innerText = "A enviar...";

            fetch(urlReenviar, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({}) 
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    const erroAntigo = document.getElementById('erro-codigo-box');
                    if (erroAntigo) erroAntigo.remove();

                    let countdown = 30;
                    const interval = setInterval(() => {
                        btnReenviar.innerText = `Código enviado! Aguarde ${countdown}s`;
                        btnReenviar.style.color = '#aaa';
                        countdown--;
                        if (countdown < 0) {
                            clearInterval(interval);
                            btnReenviar.disabled = false;
                            btnReenviar.style.color = '';
                            btnReenviar.innerText = "Código não chegou? Clique aqui para enviar novamente";
                        }
                    }, 1000);
                }
            })
            .catch(error => {
                btnReenviar.disabled = false;
                btnReenviar.innerText = "Código não chegou? Clique aqui para enviar novamente";
                exibirErroCustomizado(error.message || "Erro ao processar o reenvio do e-mail.");
            });
        });
    }
});
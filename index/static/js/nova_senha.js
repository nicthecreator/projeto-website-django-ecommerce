document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('novaSenhaForm');
    const inputSenha = document.getElementById('senha');
    const inputConfirma = document.getElementById('confirma_senha');
    
    // 1. Alternar visualização das palavras-passe (Olho)
    function configurarOlho(botaoId, inputElement) {
        const btn = document.getElementById(botaoId);
        if (btn && inputElement) {
            btn.addEventListener('click', function() {
                const tipo = inputElement.getAttribute('type') === 'password' ? 'text' : 'password';
                inputElement.setAttribute('type', tipo);
                this.classList.toggle('fa-eye');
                this.classList.toggle('fa-eye-slash');
            });
        }
    }
    configurarOlho('toggleSenha', inputSenha);
    configurarOlho('toggleConfirma', inputConfirma);

    // 2. Exibição unificada de caixas de erro estilizadas
    function exibirErroCustomizado(mensagem) {
        const erroAntigo = document.getElementById('erro-redefinicao-box');
        if (erroAntigo) erroAntigo.remove();

        const divErro = document.createElement('div');
        divErro.id = 'erro-redefinicao-box';
        divErro.style.cssText = "background-color: #fee2e2; color: #dc2626; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; font-size: 14px; width: 100%; box-sizing: border-box;";
        divErro.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> ${mensagem}`;

        const h1 = document.querySelector('.login-section h1');
        if (h1) h1.insertAdjacentElement('afterend', divErro);
    }

    // 3. Submissão assíncrona do formulário
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();

            const senha = inputSenha.value;
            const confirmaSenha = inputConfirma.value;
            const regexSenha = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/;

            if (senha !== confirmaSenha) {
                exibirErroCustomizado("As senhas informadas não coincidem.");
                return;
            }

            if (!regexSenha.test(senha)) {
                exibirErroCustomizado("A senha não cumpre os requisitos de letras maiúsculas, minúsculas e números.");
                return;
            }

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const btnSubmit = form.querySelector('.btn-entrar');
            
            btnSubmit.disabled = true;
            btnSubmit.innerText = 'A atualizar...';

            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ senha: senha, confirma_senha: confirmaSenha })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Limpa elementos de interface desnecessários
                    const erroAntigo = document.getElementById('erro-redefinicao-box');
                    if (erroAntigo) erroAntigo.remove();

                    // Altera dinamicamente o ecrã para o estado de confirmação com caixa verde
                    const loginBox = document.querySelector('.login-box');
                    if (loginBox) {
                        loginBox.innerHTML = `
                            <div style="text-align: center; padding: 10px 0;">
                                <h1 style="color: #16a34a; font-size: 26px; margin-bottom: 15px;">
                                    <i class="fa-solid fa-circle-check"></i> Senha atualizada!
                                </h1>
                                <p style="color: #444; font-size: 14px; margin-bottom: 25px; line-height: 1.5;">
                                    A sua credencial foi redefinida com sucesso no sistema.
                                </p>
                                <a href="${data.redirect_url || '/login/'}" class="btn-entrar" style="display: block; text-decoration: none; box-sizing: border-box;">
                                    Acessar minha conta
                                </a>
                            </div>
                        `;
                    }
                }
            })
            .catch(error => {
                btnSubmit.disabled = false;
                btnSubmit.innerText = 'Atualizar Palavra-passe';
                exibirErroCustomizado(error.message || "Não foi possível concluir a operação.");
            });
        });
    }
});
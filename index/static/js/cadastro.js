// home/js/registro.js

// Lógica de autocompletar da matrícula
document.addEventListener('DOMContentLoaded', function() {
    const matriculaInput = document.getElementById('matricula');
    if (matriculaInput) {
        // Bloqueia letras e limita a 6 dígitos em tempo real
        matriculaInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/\D/g, '').substring(0, 6);
        });

        matriculaInput.addEventListener('blur', function() {
            const matricula = this.value.trim();
            const msgBox = document.getElementById('matricula-msg');
            const nomeInput = document.getElementById('nome');
            const emailInput = document.getElementById('email');

            if (matricula.length > 0) {
                msgBox.textContent = 'Buscando colaborador...';
                msgBox.style.color = '#1d3557';

                fetch(`/buscar-colaborador/?matricula=${matricula}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            msgBox.textContent = 'Colaborador encontrado! Preenchendo dados...';
                            msgBox.style.color = '#16a34a';
                            
                            nomeInput.value = data.nome;
                        } else {
                            msgBox.textContent = data.message || 'Erro ao buscar matrícula.';
                            msgBox.style.color = '#dc2626';
                            nomeInput.value = '';
                        }
                    })
                    .catch(error => {
                        msgBox.textContent = 'Erro de conexão.';
                        msgBox.style.color = '#dc2626';
                    });
            } else {
                msgBox.textContent = '';
                nomeInput.value = '';
            }
        });
    }
});

// Lógica para alternar a visibilidade da senha (ativodo tanto na página de login quanto na de criação de conta para reutilização)
function toggleVisibility(fieldId) {
    const input = document.getElementById(fieldId);
    const icon = input.nextElementSibling;
    
    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = "password";
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

document.getElementById('registerForm').addEventListener('submit', function(event) {
    const senha = document.getElementById('senha').value;
    const confirmaSenha = document.getElementById('confirma_senha').value;
    
    // Expressão regular para validar: 1 maiúscula, 1 minúscula e 1 número
    const regexSenha = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/;

    // Função interna para gerar a caixa de erro com o mesmo design do Django
    function exibirErroCustomizado(mensagem) {
        // 1. Remove o erro anterior se o usuário tentar novamente
        const erroAntigo = document.getElementById('erro-cadastro-box');
        if (erroAntigo) erroAntigo.remove();

        // 2. Cria o elemento div contendo os estilos inline idênticos ao do cadastro/login
        const divErro = document.createElement('div');
        divErro.id = 'erro-cadastro-box';
        divErro.style.cssText = "background-color: #fee2e2; color: #dc2626; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; font-size: 14px;";
        
        // 3. Insere o ícone do Font Awesome e o texto descritivo
        divErro.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> ${mensagem}`;

        // 4. Localiza o H1 e insere a div logo após ele
        const h1 = document.querySelector('.login-box h1');
        h1.insertAdjacentElement('afterend', divErro);
    }

    // Validação de igualdade das senhas
    if (senha !== confirmaSenha) {
        event.preventDefault(); // Bloqueia o envio do formulário
        exibirErroCustomizado('As senhas não coincidem.');
        return;
    }

    // Validação de complexidade da senha
    if (!regexSenha.test(senha)) {
        event.preventDefault(); // Bloqueia o envio do formulário
        exibirErroCustomizado('A senha deve conter pelo menos 1 letra maiúscula, 1 letra minúscula e 1 número.');
        return;
    }
});
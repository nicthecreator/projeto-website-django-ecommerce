// 1. Mostrar/Ocultar Senha
const togglePassword = document.getElementById('togglePassword');
const senhaInput = document.getElementById('senha');

if (togglePassword && senhaInput) {
    togglePassword.addEventListener('click', function() {
        // Alterna o tipo do input entre 'password' (oculto) e 'text' (visível)
        const tipo = senhaInput.getAttribute('type') === 'password' ? 'text' : 'password';
        senhaInput.setAttribute('type', tipo);
        
        // Alterna o ícone (olho aberto / olho fechado)
        this.classList.toggle('fa-eye');
        this.classList.toggle('fa-eye-slash');
    });
}

// Executa a lógica de login ao submeter o formulário
document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); 

    const matricula = document.getElementById('matricula').value;
    const senha = document.getElementById('senha').value;
    
    // CAPTURA SE O CHECKBOX ESTÁ MARCADO (retorna true ou false)
    const lembrar = document.getElementById('lembrar').checked;
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const url = this.getAttribute('action') || '/login/';

    // Envia os dados, incluindo a propriedade 'lembrar'
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ 
            matricula: matricula, 
            senha: senha, 
            lembrar: lembrar 
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect_url;
        }
    })
    .catch(error => {
        const erroAntigo = document.getElementById('erro-login-box');
        if (erroAntigo) erroAntigo.remove();

        const divErro = document.createElement('div');
        divErro.id = 'erro-login-box';
        divErro.style.cssText = "background-color: #fee2e2; color: #dc2626; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; font-size: 14px;";
        
        const mensagemErro = error.message || 'Matrícula ou senha incorretos.';
        divErro.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> ${mensagemErro}`;

        const h1 = document.querySelector('.login-box h1');
        h1.insertAdjacentElement('afterend', divErro);
    });
});

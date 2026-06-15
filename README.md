# PHD Store - E-commerce Web Application

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

Um sistema completo de e-commerce construído com **Python e Django** no back-end, e uma interface moderna e assíncrona utilizando **JavaScript vanilla (Fetch API)**, HTML5 e CSS3 no front-end. O projeto foca em segurança, validação de dados e uma experiência de usuário fluida sem recarregamento desnecessário de páginas.

---

## ✨ Funcionalidades

* **Autenticação Customizada:** Sistema de login e registro de usuários com validação estrita.
* **Segurança de Senhas:** Validação de complexidade (mínimo de 6 caracteres, letras maiúsculas, minúsculas e números) tratada tanto no Front-end (Regex JS) quanto no Back-end (Python `re`).
* **Verificação de E-mail (2FA):** Envio de código de 6 dígitos para ativação de contas inativas (`is_active=False`), com temporizador anti-spam para reenvio.
* **Recuperação de Senha Segura:** Geração de links únicos e temporários baseados em tokens criptografados (`uidb64` e `default_token_generator`).
* **Sessões Inteligentes:** Funcionalidade "Lembrar de mim" manipulando a expiração de cookies no servidor.
* **Painel de Usuário (Dashboard):** Layout responsivo estruturado em Flexbox com menu lateral dinâmico.
* **Feedback Visual Integrado:** Alertas de sucesso e erro injetados dinamicamente na DOM via JavaScript, substituindo pop-ups nativos do navegador.

---

## 💻 Tecnologias Utilizadas

* **Back-end:** Python 3, Django (Sem uso de Flask ou microframeworks).
* **Front-end:** HTML5, CSS3 (Flexbox), JavaScript Vanilla.
* **Comunicação:** Fetch API e JSON para requisições assíncronas (AJAX).
* **Banco de Dados:** SQLite (padrão de desenvolvimento, pronto para migração PostgreSQL em produção).

---

## 🚀 Como Executar o Projeto Localmente

Siga as instruções abaixo para rodar o ambiente de desenvolvimento na sua máquina.

### Pré-requisitos
* [Python 3.x](https://www.python.org/downloads/) instalado.
* [Git](https://git-scm.com/) instalado.

### Passo a Passo

1. ### Clone o repositório:
```bash
   git clone https://github.com/nicthecreator/projeto-website-django-ecommerce.git
   cd projeto-website-django-ecommerce
   ```
   
2. ### Crie e ative um ambiente virtual (VENV):

**No Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**No Linux/macOS**
```bash    
python3 -m venv venv
source venv/bin/activate
```

3. ### Instale as dependências:

```bash
pip install django
# Caso exista um requirements.txt: pip install -r requirements.txt
```

4. ### Realize as migrações do banco de dados:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. ### Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

*O site estará disponível em `http://127.0.0.1:8000/`.*

   > **Aviso sobre E-mails:** No ambiente de desenvolvimento local, o sistema de envio de e-mails (como os códigos de verificação e links de senha) está configurado para o terminal (`console.EmailBackend`). O código será impresso no prompt de comando onde o servidor está rodando.

---

## 🔍 Destaques de Arquitetura (Front/Back)

Para manter a segurança e a velocidade, o sistema divide rigidamente as responsabilidades. 

**Validação no Front-end (JavaScript):**
```javascript
// Interceptação assíncrona para feedback imediato e estilizado
const regexSenha = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/;
if (!regexSenha.test(senha)) {
    exibirErroCustomizado("A senha não atende aos requisitos de segurança.");
    return;
}
```
 ## 👥 👨‍💻 Autor
Desenvolvido por **Nicolas Gabriel Barbosa de Ursino**
como parte dos estudos práticos em Engenharia de Software e Desenvolvimento de Sistemas.

---
*Brasília, 2026*

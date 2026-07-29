# PHD Store - Plataforma B2B de Logística e E-commerce

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

Um sistema robusto e completo desenvolvido para gerenciar produtos, controle de limites e gestão logística interna. Construído com **Python e Django** no back-end, e uma interface moderna utilizando **JavaScript vanilla, HTML5 e CSS3** no front-end. 

O projeto é focado em segurança, validação de dados, experiência do usuário e otimização de processos corporativos.

---

## ✨ Funcionalidades Principais

* **Gestão e Importação de Produtos em Lote:** 
  * Cadastro manual de produtos com suporte a edição avançada de imagens (corte quadrado em tempo real via `Cropper.js`).
  * **Integração com Excel (`openpyxl`):** Funcionalidade nativa para importar dezenas de produtos automaticamente via upload de arquivo `.xlsx`, com tratamento inteligente de formatação.
* **Sistema de Pedidos e Kanban Logístico:** 
  * Controle de pedidos (retiradas) separados por filiais (Goiânia e Brasília).
  * Painel Administrativo com visão Kanban (Aguardando Retirada -> Enviado -> Pronto -> Retirado).
  * Impressão automática de **Guias de Remessa** estilizadas para controle físico de pacotes.
* **Autenticação Customizada e Segura:**
  * Sistema de login e registro de usuários com validação estrita.
  * Validação de senhas complexas tanto no Front-end (Regex JS) quanto no Back-end.

* **Painel do Funcionário (Dashboard):** 
  * Controle inteligente do "Limite por Ciclo/Folha", impedindo que funcionários retirem mais produtos do que o permitido pelas regras da empresa.
  * Histórico de pedidos e acompanhamento de status em tempo real.
* **Relatórios e Fechamento (Módulo RH):**
  * Tela dedicada para o RH com listagem agrupada por funcionário e geração do total devido para desconto em folha.
  * Sistema de "Baixa" com registro automático de quem deu a baixa e a data exata, zerando o ciclo do funcionário.

---

## 💻 Tecnologias Utilizadas

* **Back-end:** Python 3, Django, OpenPyXL (Leitura de planilhas).
* **Front-end:** HTML5, CSS3, JavaScript Vanilla, Cropper.js (Edição de imagens).
* **Banco de Dados:** PostgreSQL (Produção/Nuvem) e SQLite (Desenvolvimento local).
* **Infraestrutura e Deploy:** 
  * Deploy otimizado na plataforma **Railway**.
  * Servidor web **Gunicorn**.
  * Compressão e entrega de arquivos estáticos via **WhiteNoise**.

---

## 🚀 Como Executar o Projeto Localmente

Siga as instruções abaixo para rodar o ambiente de desenvolvimento na sua máquina.

### Pré-requisitos
* [Python 3.x](https://www.python.org/downloads/) instalado.
* [Git](https://git-scm.com/) instalado.

### Passo a Passo

1. **Clone o repositório:**
```bash
git clone https://github.com/nicthecreator/projeto-website-django-ecommerce.git
cd projeto-website-django-ecommerce
```

2. **Crie e ative um ambiente virtual (VENV):**

*No Windows:*
```bash
python -m venv venv
venv\Scripts\activate
```
*No Linux/macOS:*
```bash    
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências principais:**
```bash
pip install -r requirements.txt
```

4. **Realize as migrações do banco de dados (SQLite):**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Inicie o servidor de desenvolvimento:**
```bash
python manage.py runserver
```
*O site estará disponível em `http://127.0.0.1:8000/`.*



---

## 🌐 Deploy em Produção (Nuvem)

Este projeto está configurado para Deploy contínuo via Nixpacks na plataforma **Railway**.

**Configurações do Start Command utilizadas:**
```bash
python manage.py migrate && gunicorn project.wsgi --workers 2 --threads 4 --worker-class gthread
```

As variáveis de ambiente (`SECRET_KEY`, `DATABASE_URL`, `DEBUG=False`, `ALLOWED_HOSTS`) devem ser injetadas diretamente nas configurações do Railway. 
O Django utilizará automaticamente o **dj-database-url** para converter a URL do banco para a conexão segura com o PostgreSQL e o **WhiteNoise** para comprimir arquivos estáticos (CSS/JS) diretamente do contêiner.

---

## 👥 👨‍💻 Autor
Desenvolvido por **Nicolas Gabriel Barbosa de Ursino**
*Brasília, 2026*

from django.shortcuts import render, redirect # Importação para renderizar templates HTML e redirecionar usuários para outras páginas
from django.contrib.auth.models import User # Importação do modelo de usuário padrão do Django para criar e gerenciar usuários
from django.contrib.auth import authenticate, login # Importação para autenticação e login do usuário
from django.contrib import messages # Importação para exibir mensagens de sucesso ou erro para o usuário
from django.http import JsonResponse # Importação para retornar respostas JSON em requisições AJAX
import json # Importação para lidar com dados JSON enviados via AJAX
from django.contrib.auth import logout # Importação para logout
from django.contrib.auth.decorators import login_required # Importação para proteger a view de perfil
import re # Importação para expressões regulares (validação de e-mail)
import random # Importação para geração de código aleatório
from django.core.mail import send_mail # Importação para envio de e-mails
from django.contrib.auth.tokens import default_token_generator # Importação para geração de tokens seguros (usado em recuperação de senha)
from django.utils.http import urlsafe_base64_encode # Importação para codificar o ID do usuário em base64 para inclusão em URLs
from django.utils.encoding import force_bytes # Importação para converter dados em bytes (necessário para codificação base64)
from django.utils.http import urlsafe_base64_decode # Importação para decodificar o ID do usuário a partir da URL
from django.utils.encoding import force_str # Importação para converter bytes de volta para string (necessário após decodificação base64

# MVT (MVC) => Model View Template (Controller)

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            senha = data.get('senha')
            # Recupera a preferência do usuário (padrão é False se não enviado)
            lembrar = data.get('lembrar', False)

            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=senha)
            except User.DoesNotExist:
                user = None

            if user is not None:
                login(request, user)
                
                # CONFIGURAÇÃO DA SESSÃO VIA DJANGO
                if lembrar:
                    # 1209600 segundos correspondem a exatamente 2 semanas mantendo o usuário logado
                    request.session.set_expiry(1209600)
                else:
                    # 0 significa que a sessão expira assim que o usuário fecha o navegador
                    request.session.set_expiry(0)

                return JsonResponse({'success': True, 'redirect_url': '/'})
            else:
                return JsonResponse({'success': False, 'message': 'E-mail ou senha incorretos.'}, status=401)
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Erro interno no servidor.'}, status=500)

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('index')


def cadastro_view(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    else:
        # O strip() remove espaços vazios que o usuário digite sem querer
        nome = request.POST.get('nome').strip() 
        # O lower() força o e-mail a ficar todo em minúsculo, padronizando a verificação
        email = request.POST.get('email').strip().lower()
        senha = request.POST.get('senha')
        confirma_senha = request.POST.get('confirma_senha')

        # ... (suas validações de campos vazios e senhas continuam aqui) ...

        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            return render(request, 'cadastro.html', {'error': 'E-mail já cadastrado.'})

        try:
            # 1. Cria o usuário como INATIVO (is_active=False)
            user = User.objects.create_user(
                username=email, 
                email=email, 
                password=senha,
                first_name=nome,
                is_active=False # O usuário não consegue logar ainda
            )
            user.save()

            # 2. Gera um código de 6 dígitos aleatório
            codigo = str(random.randint(100000, 999999))
            
            # 3. Salva o código e o e-mail na sessão do navegador temporariamente
            request.session['codigo_verificacao'] = codigo
            request.session['email_verificacao'] = email

            # 4. Dispara o e-mail para o usuário
            send_mail(
                'Confirme sua conta - PHD Store',
                f'Olá, {nome}! Seu código de verificação é: {codigo}',
                'nao-responda@phdstore.com', # Remetente
                [email],                     # Destinatário
                fail_silently=False,
            )

            # Redireciona para a tela de digitar o código
            return redirect('verificar_codigo')
            
        except Exception as e:
            return render(request, 'cadastro.html', {'error': f'Erro interno: {str(e)}'})
        

# Nova View para processar o código digitado
def verificar_codigo_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            codigo_digitado = data.get('codigo')
            
            # Resgata os dados que guardamos na sessão durante o cadastro
            email_sessao = request.session.get('email_verificacao')
            codigo_sessao = request.session.get('codigo_verificacao')

            if not email_sessao or not codigo_sessao:
                return JsonResponse({'success': False, 'message': 'Sessão expirada. Refaça o cadastro.'}, status=400)

            # Verifica se o código bate com o gerado
            if codigo_digitado == codigo_sessao:
                # Encontra o usuário inativo e o ativa
                user = User.objects.get(email=email_sessao)
                user.is_active = True
                user.save()
                
                # Limpa a sessão por segurança
                del request.session['codigo_verificacao']
                del request.session['email_verificacao']
                
                return JsonResponse({'success': True, 'redirect_url': '/login/'})
            else:
                return JsonResponse({'success': False, 'message': 'Código inválido.'}, status=400)
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Erro no servidor.'}, status=500)

    # Se for GET, apenas mostra a página HTML
    return render(request, 'verificar_codigo.html')

def reenviar_codigo_view(request):
    if request.method == 'POST':
        # Busca o e-mail armazenado temporariamente na sessão do usuário
        email = request.session.get('email_verificacao')
        
        if not email:
            return JsonResponse({
                'success': False, 
                'message': 'Sessão expirada. Por favor, realize o cadastro novamente.'
            }, status=400)

        # Atualiza o código para um novo valor aleatório
        novo_codigo = str(random.randint(100000, 999999))
        request.session['codigo_verificacao'] = novo_codigo

        try:
            send_mail(
                'Novo Código de Verificação - PHD Store',
                f'Seu novo código de verificação é: {novo_codigo}',
                'nao-responda@phdstore.com',
                [email],
                fail_silently=False,
            )
            return JsonResponse({'success': True, 'message': 'Novo código enviado!'})
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': 'Ocorreu um erro no servidor de e-mail ao tentar reenviar.'
            }, status=500)

def recuperar_senha_view(request):
    if request.method == 'POST':
        try:
            # Captura o e-mail enviado pelo JavaScript (Fetch API)
            data = json.loads(request.body)
            email = data.get('email')

            # Procura o usuário no banco de dados
            user = User.objects.filter(email=email).first()

            if user:
                # 1. Gera uma identificação criptografada e um Token
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                # 2. Monta o link com o domínio atual (ex: 127.0.0.1:8000)
                dominio = request.get_host()
                link = f"http://{dominio}/nova-senha/{uid}/{token}/"

                # 3. Dispara o e-mail simulado para o terminal
                send_mail(
                    'Recuperação de Senha - PHD Store',
                    f'Olá, {user.first_name}!\n\nRecebemos um pedido para redefinir sua senha.\nClique no link abaixo para criar uma nova senha:\n\n{link}\n\nSe você não solicitou isso, ignore este e-mail.',
                    'nao-responda@phdstore.com',
                    [email],
                    fail_silently=False,
                )

            # Devolve um JSON que o JavaScript consegue ler (evitando o erro '<')
            return JsonResponse({
                'success': True, 
                'message': 'Se o e-mail estiver cadastrado, você receberá um link em instantes.'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Erro ao processar a solicitação.'}, status=500)

    # Se for apenas o carregamento normal da página (GET)
    return render(request, 'recuperar_senha.html')

def nova_senha_view(request, uidb64, token):
    try:
        # Descodifica o ID do utilizador enviado na URL
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Valida se o utilizador existe e se o token de segurança está correto e dentro do prazo
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                senha = data.get('senha')
                confirma_senha = data.get('confirma_senha')

                # Validações de segurança no servidor
                if not senha or not confirma_senha:
                    return JsonResponse({'success': False, 'message': 'Todos os campos são obrigatórios.'}, status=400)
                if senha != confirma_senha:
                    return JsonResponse({'success': False, 'message': 'As senhas não coincidem.'}, status=400)
                if len(senha) < 6:
                    return JsonResponse({'success': False, 'message': 'A senha deve conter pelo menos 6 caracteres.'}, status=400)
                if not re.search(r'[A-Z]', senha) or not re.search(r'[a-z]', senha) or not re.search(r'\d', senha):
                    return JsonResponse({'success': False, 'message': 'A senha deve conter pelo menos 1 letra maiúscula, 1 letra minúscula e 1 número.'}, status=400)

                # Define e criptografa a nova palavra-passe no banco de dados
                user.set_password(senha)
                user.save()

                return JsonResponse({
                    'success': True, 
                    'message': 'Palavra-passe alterada com sucesso!',
                    'redirect_url': '/login/'
                })
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Erro interno ao processar a redefinição.'}, status=500)

        # Se a requisição for GET e o token for válido, exibe o formulário
        return render(request, 'nova_senha.html', {'token_valido': True})
    else:
        # Se o link for inválido ou já tiver sido utilizado, renderiza com aviso de erro
        return render(request, 'nova_senha.html', {'token_valido': False})


def index_view(request):
    # Exemplo de contexto que viria do seu banco de dados
    produtos = [
        {
            'nome': 'Biscoito Amanteigado Gourmet',
            'avaria': 'Embalagem Amassada',
            'preco_original': 15.90,
            'preco_desconto': 5.90,
            'imagem_url': 'https://via.placeholder.com/200x200?text=Biscoito'
        },
        {
            'nome': 'Azeite de Oliva Extra Virgem 500ml',
            'avaria': 'Rótulo Rasgado',
            'preco_original': 45.90,
            'preco_desconto': 22.90,
            'imagem_url': 'https://via.placeholder.com/200x200?text=Azeite'
        },
        {
            'nome': 'Macarrão Penne Grano Duro 500g',
            'avaria': 'Caixa Danificada',
            'preco_original': 8.50,
            'preco_desconto': 3.50,
            'imagem_url': 'https://via.placeholder.com/200x200?text=Macarrao'
        },
        {
            'nome': 'Leite Integral 1L',
            'avaria': 'Embalagem Amassada',
            'preco_original': 15.90,
            'preco_desconto': 5.90,
            'imagem_url': 'https://via.placeholder.com/200x200?text=Biscoito'
        },
        {
            'nome': 'Leite Condensado 395g',
            'avaria': 'Rótulo Rasgado',
            'preco_original': 45.90,
            'preco_desconto': 22.90,
            'imagem_url': 'https://via.placeholder.com/200x200?text=Azeite'
        },
        {
            'nome': 'Arroz Branco Tipo 1 5kg',
            'avaria': 'Caixa Danificada',
            'preco_original': 8.50,
            'preco_desconto': 3.50,
            'imagem_url': 'https://via.placeholder.com/200x200?text=Macarrao'
        },
        {
            'nome': 'Macarrão Penne Grano Duro 500g',
            'avaria': 'Caixa Danificada',
            'preco_original': 8.50,
            'preco_desconto': 3.50,
            'imagem_url': 'https://via.placeholder.com/200x200?text=Macarrao'
        },
        {
            'nome': 'Leite Integral 1L',
            'avaria': 'Embalagem Amassada',
            'preco_original': 15.90,
            'preco_desconto': 5.90,
            'imagem_url': 'https://via.placeholder.com/200x200?text=Biscoito'
        },
        {
            'nome': 'Leite Condensado 395g',
            'avaria': 'Rótulo Rasgado',
            'preco_original': 45.90,
            'preco_desconto': 22.90,
            'imagem_url': 'https://via.placeholder.com/200x200?text=Azeite'
        },
        {
            'nome': 'Arroz Branco Tipo 1 5kg',
            'avaria': 'Caixa Danificada',
            'preco_original': 8.50,
            'preco_desconto': 3.50,
            'imagem_url': 'https://via.placeholder.com/200x200?text=Macarrao'
        },
        {
            'nome': 'Arroz Branco Tipo 1 5kg',
            'avaria': 'Caixa Danificada',
            'preco_original': 8.50,
            'preco_desconto': 3.50,
            'imagem_url': 'https://via.placeholder.com/200x200?text=Macarrao'
        },
        {
            'nome': 'Arroz Branco Tipo 1 5kg',
            'avaria': 'Caixa Danificada',
            'preco_original': 8.50,
            'preco_desconto': 3.50,
            'imagem_url': 'https://via.placeholder.com/200x200?text=Macarrao'
        }
    ]
    
    return render(request, 'index.html', {'produtos': produtos})


@login_required(login_url='login') # Garante que só quem está logado acesse
def perfil_view(request):
    if request.method == 'POST':
        try:
            # Captura o novo nome do formulário
            novo_nome = request.POST.get('nome')
            
            # Atualiza o modelo de usuário padrão do Django
            usuario = request.user
            usuario.first_name = novo_nome
            usuario.save()
            
            # Se você criar um modelo 'Perfil' depois para telefone/localização, 
            # você o salvaria aqui. Ex:
            # perfil = usuario.perfil
            # perfil.telefone = request.POST.get('telefone')
            # perfil.save()

            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')
            
        except Exception as e:
            messages.error(request, 'Erro ao atualizar o perfil.')
            
    return render(request, 'perfil.html')

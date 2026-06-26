from django.shortcuts import render, redirect, get_object_or_404 # Importação para renderizar templates HTML e redirecionar usuários para outras páginas
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


from .models import Colaborador, UserProfile

def buscar_colaborador(request):
    matricula = request.GET.get('matricula')
    if not matricula:
        return JsonResponse({'success': False, 'message': 'Matrícula não informada.'})
    
    try:
        colaborador = Colaborador.objects.get(matricula=matricula)
        # Verifica se alguém já se cadastrou com essa matrícula
        if UserProfile.objects.filter(matricula=matricula).exists():
            return JsonResponse({'success': False, 'message': 'Esta matrícula já possui um cadastro.'})
            
        return JsonResponse({
            'success': True, 
            'nome': colaborador.nome, 
            'email': colaborador.email
        })
    except Colaborador.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Matrícula não encontrada no sistema.'})

def cadastro_view(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    else:
        matricula = request.POST.get('matricula', '').strip()
        nome = request.POST.get('nome', '').strip() 
        email = request.POST.get('email', '').strip().lower()
        celular = request.POST.get('celular', '').strip()
        senha = request.POST.get('senha')
        confirma_senha = request.POST.get('confirma_senha')

        if not matricula:
            return render(request, 'cadastro.html', {'error': 'Matrícula é obrigatória.'})
            
        if not Colaborador.objects.filter(matricula=matricula).exists():
            return render(request, 'cadastro.html', {'error': 'Matrícula inválida.'})

        if UserProfile.objects.filter(matricula=matricula).exists():
            return render(request, 'cadastro.html', {'error': 'Esta matrícula já está cadastrada.'})

        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            return render(request, 'cadastro.html', {'error': 'E-mail já cadastrado.'})

        try:
            # Em vez de sujar o banco de dados agora, salvamos na sessão
            request.session['cadastro_data'] = {
                'matricula': matricula,
                'nome': nome,
                'email': email,
                'celular': celular,
                'senha': senha
            }

            # Gera um código de 6 dígitos aleatório
            codigo = str(random.randint(100000, 999999))
            
            # Salva o código e o e-mail na sessão do navegador
            request.session['codigo_verificacao'] = codigo
            request.session['email_verificacao'] = email

            # Dispara o e-mail para o usuário
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
            cadastro_data = request.session.get('cadastro_data')

            if not email_sessao or not codigo_sessao or not cadastro_data:
                return JsonResponse({'success': False, 'message': 'Sessão expirada. Refaça o cadastro.'}, status=400)

            # Verifica se o código bate com o gerado
            if codigo_digitado == codigo_sessao:
                # Verifica novamente se já existe (segurança extra)
                if UserProfile.objects.filter(matricula=cadastro_data['matricula']).exists():
                    return JsonResponse({'success': False, 'message': 'Matrícula já cadastrada no meio tempo.'}, status=400)
                    
                # Cria o usuário finalmente como ATIVO
                user = User.objects.create_user(
                    username=cadastro_data['email'],
                    email=cadastro_data['email'],
                    password=cadastro_data['senha'],
                    first_name=cadastro_data['nome'],
                    is_active=True
                )
                
                UserProfile.objects.create(
                    user=user,
                    matricula=cadastro_data['matricula'],
                    celular=cadastro_data['celular']
                )
                
                # Faz login automaticamente
                from django.contrib.auth import login
                login(request, user)
                
                # Limpa a sessão
                del request.session['codigo_verificacao']
                del request.session['email_verificacao']
                del request.session['cadastro_data']
                
                return JsonResponse({'success': True, 'redirect_url': '/'})
            else:
                return JsonResponse({'success': False, 'message': 'Código inválido.'}, status=400)
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro no servidor: {str(e)}'}, status=500)

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
    # Busca produtos com estoque maior que zero
    produtos = Produto.objects.filter(estoque__gt=0).order_by('-id')
    
    return render(request, 'index.html', {'produtos': produtos})


@login_required(login_url='login') # Garante que só quem está logado acesse
def perfil_view(request):
    if request.method == 'POST':
        try:
            # Captura o novo celular do formulário
            novo_celular = request.POST.get('celular')
            
            # Atualiza o modelo de perfil do usuário
            perfil = request.user.profile
            perfil.celular = novo_celular
            perfil.save()
            
            messages.success(request, 'Celular atualizado com sucesso!')
            return redirect('perfil')
            
        except Exception as e:
            messages.error(request, 'Erro ao atualizar o perfil.')
            
    return render(request, 'perfil.html')

from .models import Pedido, ItemPedido

from datetime import timedelta
from django.db.models import Sum

@login_required(login_url='login')
def verificar_limite_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            produto_id = data.get('produto_id')
            qtd_solicitada = int(data.get('quantidade', 1))
            
            if not produto_id:
                return JsonResponse({'success': False, 'message': 'Produto não informado.'})
                
            try:
                produto = Produto.objects.get(id=produto_id)
            except Produto.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Produto não encontrado.'})
                
            agora = timezone.now()
            limite_24h = agora - timedelta(hours=24)
            
            compras_24h = ItemPedido.objects.filter(
                pedido__usuario=request.user,
                produto=produto,
                pedido__data_pedido__gte=limite_24h
            ).exclude(pedido__status='Cancelado').aggregate(total_comprado=Sum('quantidade'))['total_comprado'] or 0
            
            if (compras_24h + qtd_solicitada) > produto.limite_por_funcionario:
                return JsonResponse({
                    'success': False, 
                    'message': f'O limite do produto "{produto.nome}" são {produto.limite_por_funcionario} unidades em 24h.'
                })
                
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Método inválido.'})

@login_required(login_url='login')
def checkout_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            itens = data.get('itens', [])
            total = data.get('total', 0)
            
            if not itens:
                return JsonResponse({'success': False, 'message': 'O carrinho está vazio.'}, status=400)
                
            # Validar limites de 24h
            agora = timezone.now()
            limite_24h = agora - timedelta(hours=24)
            
            produtos_validados = []
            
            for item in itens:
                produto_id = item.get('id')
                if not produto_id:
                    return JsonResponse({'success': False, 'message': 'Carrinho desatualizado. Por favor, remova os itens do carrinho e adicione novamente.'}, status=400)
                    
                try:
                    produto = Produto.objects.get(id=produto_id)
                except Produto.DoesNotExist:
                    return JsonResponse({'success': False, 'message': f'Produto {item.get("nome")} não encontrado.'}, status=404)
                    
                qtd_solicitada = int(item.get('quantidade', 0))
                
                # Buscar quantidade comprada nas últimas 24h (ignorando cancelados)
                compras_24h = ItemPedido.objects.filter(
                    pedido__usuario=request.user,
                    produto=produto,
                    pedido__data_pedido__gte=limite_24h
                ).exclude(pedido__status='Cancelado').aggregate(total_comprado=Sum('quantidade'))['total_comprado'] or 0
                
                if (compras_24h + qtd_solicitada) > produto.limite_por_funcionario:
                    return JsonResponse({
                        'success': False, 
                        'message': f'O limite do produto "{produto.nome}" são {produto.limite_por_funcionario} unidades em 24h.'
                    }, status=400)
                    
                produtos_validados.append({
                    'produto': produto,
                    'nome': item.get('nome'),
                    'quantidade': qtd_solicitada,
                    'preco': item.get('preco')
                })
                
            # Cria o pedido no banco de dados
            pedido = Pedido.objects.create(
                usuario=request.user,
                total=total,
                desconto_folha=True,
                termo_aceito=True
            )
            
            # Cria os itens do pedido
            for item_val in produtos_validados:
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=item_val['produto'],
                    produto_nome=item_val['nome'],
                    quantidade=item_val['quantidade'],
                    preco_unitario=item_val['preco']
                )
                
                # Opcional: Atualizar o estoque
                # item_val['produto'].estoque -= item_val['quantidade']
                # item_val['produto'].save()
                
            return JsonResponse({
                'success': True,
                'redirect_url': f'/comprovante/{pedido.id}/'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao processar pedido: {str(e)}'}, status=500)
            
    return render(request, 'checkout.html')

@login_required(login_url='login')
def comprovante_view(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id, usuario=request.user)
        return render(request, 'comprovante.html', {'pedido': pedido})
    except Pedido.DoesNotExist:
        messages.error(request, 'Pedido não encontrado.')
        return redirect('index')

@login_required(login_url='login')
def minhas_compras_view(request):
    # Busca os pedidos do usuário, do mais recente para o mais antigo
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-data_pedido')
    return render(request, 'minhas_compras.html', {'pedidos': pedidos})

from django.utils import timezone
from .models import Produto

@login_required(login_url='login')
def painel_admin_view(request):
    if not request.user.is_staff:
        messages.error(request, 'Acesso restrito para administradores.')
        return redirect('index')
    
    produtos = Produto.objects.all().order_by('-id')
    pedidos = Pedido.objects.all().order_by('-data_pedido')
    
    return render(request, 'painel_admin.html', {'produtos': produtos, 'pedidos': pedidos})

@login_required(login_url='login')
def adicionar_produto(request):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Não autorizado'}, status=403)
        
    if request.method == 'POST':
        nome = request.POST.get('nome')
        avaria = request.POST.get('avaria')
        preco_original = request.POST.get('preco_original')
        preco_desconto = request.POST.get('preco_desconto')
        estoque = request.POST.get('estoque', 0)
        limite_por_funcionario = request.POST.get('limite_por_funcionario', 1)
        imagem_produto = request.FILES.get('imagem_produto')
        
        try:
            Produto.objects.create(
                nome=nome,
                avaria=avaria,
                preco_original=preco_original,
                preco_desconto=preco_desconto,
                estoque=estoque,
                limite_por_funcionario=limite_por_funcionario,
                imagem_produto=imagem_produto
            )
            messages.success(request, 'Produto adicionado com sucesso!')
            return redirect('painel_admin')
        except Exception as e:
            messages.error(request, f'Erro ao adicionar produto: {str(e)}')
            return redirect('painel_admin')
            
    return redirect('painel_admin')

@login_required(login_url='login')
def editar_produto(request, produto_id):
    if not request.user.is_staff:
        messages.error(request, 'Não autorizado')
        return redirect('index')
        
    if request.method == 'POST':
        try:
            produto = Produto.objects.get(id=produto_id)
            produto.nome = request.POST.get('nome')
            produto.avaria = request.POST.get('avaria')
            
            # Converte string formatada em float se necessário
            preco_original = request.POST.get('preco_original').replace(',', '.')
            preco_desconto = request.POST.get('preco_desconto').replace(',', '.')
            
            produto.preco_original = preco_original
            produto.preco_desconto = preco_desconto
            produto.estoque = request.POST.get('estoque', 0)
            produto.limite_por_funcionario = request.POST.get('limite_por_funcionario', 1)
            
            imagem_produto = request.FILES.get('imagem_produto')
            if imagem_produto:
                produto.imagem_produto = imagem_produto
                
            produto.save()
            messages.success(request, 'Produto atualizado com sucesso!')
        except Produto.DoesNotExist:
            messages.error(request, 'Produto não encontrado.')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar produto: {str(e)}')
            
    return redirect('painel_admin')

@login_required(login_url='login')
def deletar_produto(request, produto_id):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Não autorizado'}, status=403)
        
    if request.method == 'POST':
        try:
            produto = Produto.objects.get(id=produto_id)
            produto.delete()
            return JsonResponse({'success': True})
        except Produto.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Produto não encontrado'}, status=404)
            
    return JsonResponse({'success': False, 'message': 'Método inválido'}, status=405)

@login_required(login_url='login')
def dar_baixa_pedido(request, pedido_id):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Não autorizado'}, status=403)
        
    if request.method == 'POST':
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            if pedido.status == 'Pendente':
                pedido.status = 'Retirado'
                pedido.data_retirada = timezone.now()
                pedido.responsavel_retirada = request.user
                pedido.save()
                return JsonResponse({
                    'success': True, 
                    'data_retirada': pedido.data_retirada.strftime('%d/%m/%Y %H:%M'),
                    'responsavel': request.user.first_name or request.user.username
                })
            return JsonResponse({'success': False, 'message': 'Pedido já retirado ou cancelado'}, status=400)
        except Pedido.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pedido não encontrado'}, status=404)
            
    return JsonResponse({'success': False, 'message': 'Método inválido'}, status=405)

from django.db.models import Q
from datetime import datetime

@login_required(login_url='login')
def relatorio_rh_view(request):
    eh_rh = False
    try:
        if hasattr(request.user, 'profile') and request.user.profile.is_rh:
            eh_rh = True
    except Exception:
        pass
        
    if not (request.user.is_superuser or eh_rh):
        messages.error(request, 'Acesso restrito ao RH.')
        return redirect('index')

    mes = request.GET.get('mes', '')
    ano = request.GET.get('ano', '')
    
    # Filtro base ignorando cancelados
    filtro_pedidos = ~Q(pedidos__status='Cancelado')
    
    if mes:
        filtro_pedidos &= Q(pedidos__data_pedido__month=int(mes))
    if ano:
        filtro_pedidos &= Q(pedidos__data_pedido__year=int(ano))
        
    usuarios = User.objects.filter(is_active=True, is_staff=False).annotate(
        total_gasto=Sum('pedidos__total', filter=filtro_pedidos)
    ).order_by('first_name')
    
    # Lista de anos (para o filtro), pegando os anos distintos dos pedidos
    anos_disponiveis = Pedido.objects.dates('data_pedido', 'year', order='DESC')
    anos_disponiveis = [d.year for d in anos_disponiveis]
    if not anos_disponiveis:
        anos_disponiveis = [datetime.now().year]
        
    context = {
        'usuarios': usuarios,
        'mes_selecionado': mes,
        'ano_selecionado': ano,
        'anos_disponiveis': anos_disponiveis
    }
    
    return render(request, 'relatorio_rh.html', context)

@login_required(login_url='login')
def relatorio_rh_detalhes_view(request, user_id):
    eh_rh = False
    try:
        if hasattr(request.user, 'profile') and request.user.profile.is_rh:
            eh_rh = True
    except Exception:
        pass
        
    if not (request.user.is_superuser or eh_rh):
        messages.error(request, 'Acesso restrito ao RH.')
        return redirect('index')

    funcionario = get_object_or_404(User, id=user_id)
    
    mes = request.GET.get('mes', '')
    ano = request.GET.get('ano', '')
    
    pedidos = Pedido.objects.filter(usuario=funcionario).exclude(status='Cancelado')
    
    if mes:
        pedidos = pedidos.filter(data_pedido__month=int(mes))
    if ano:
        pedidos = pedidos.filter(data_pedido__year=int(ano))
        
    pedidos = pedidos.order_by('-data_pedido').prefetch_related('itens', 'itens__produto')
    
    total_gasto = pedidos.aggregate(Sum('total'))['total__sum'] or 0.00
    
    context = {
        'funcionario': funcionario,
        'pedidos': pedidos,
        'mes_selecionado': mes,
        'ano_selecionado': ano,
        'total_gasto': total_gasto
    }
    return render(request, 'relatorio_rh_detalhes.html', context)

@login_required(login_url='login')
def dar_baixa_rh_view(request, pedido_id):
    eh_rh = False
    try:
        if hasattr(request.user, 'profile') and request.user.profile.is_rh:
            eh_rh = True
    except Exception:
        pass
        
    if not (request.user.is_superuser or eh_rh):
        return JsonResponse({'success': False, 'message': 'Não autorizado'}, status=403)
        
    if request.method == 'POST':
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            pedido.descontado_rh = True
            pedido.responsavel_baixa = request.user
            pedido.save()
            return JsonResponse({
                'success': True, 
                'status': 'baixado',
                'responsavel': request.user.first_name or request.user.username
            })
        except Pedido.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pedido não encontrado'}, status=404)
            
    return JsonResponse({'success': False, 'message': 'Método inválido'}, status=405)
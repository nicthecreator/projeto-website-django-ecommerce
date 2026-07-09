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
import base64
from django.core.files.base import ContentFile
import uuid

# MVT (MVC) => Model View Template (Controller)

# Create your views here.

from .models import Colaborador, UserProfile, Produto, Pedido, ItemPedido
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            matricula = data.get('matricula')
            senha = data.get('senha')
            lembrar = data.get('lembrar', False)

            if not matricula or not senha:
                return JsonResponse({'success': False, 'message': 'Matrícula e senha são obrigatórios.'}, status=400)

            # 1. Encontra o perfil do usuário correspondente à matrícula
            user_profile = UserProfile.objects.filter(matricula=matricula).first()
            user = None

            if user_profile:
                # Usuário antigo/existente
                user = authenticate(request, username=user_profile.user.username, password=senha)
                
                # Se falhar, pode ser que a senha atual seja diferente do CPF (já que era livre antes)
                # Como a regra mudou, vamos checar se a senha digitada bate com os 5 primeiros do CPF.
                # Se bater, corrigimos a senha dele e logamos.
                if user is None:
                    try:
                        colaborador = Colaborador.objects.get(matricula=matricula)
                        if colaborador.cpf and senha == colaborador.cpf[:5]:
                            user_profile.user.set_password(senha)
                            user_profile.user.save()
                            user = authenticate(request, username=user_profile.user.username, password=senha)
                    except Colaborador.DoesNotExist:
                        pass
            else:
                # Usuário novo (não tem UserProfile)
                try:
                    colaborador = Colaborador.objects.get(matricula=matricula)
                    if colaborador.cpf and senha == colaborador.cpf[:5]:
                        user = User.objects.create_user(
                            username=matricula,
                            email=f"{matricula}@phdstore.com",
                            password=senha,
                            first_name=colaborador.nome,
                            is_active=True
                        )
                        UserProfile.objects.create(user=user, matricula=matricula)
                        user = authenticate(request, username=matricula, password=senha)
                except Colaborador.DoesNotExist:
                    pass

            if user is not None:
                login(request, user)
                if lembrar:
                    request.session.set_expiry(1209600)
                else:
                    request.session.set_expiry(0)
                return JsonResponse({'success': True, 'redirect_url': '/loja/'})
            else:
                return JsonResponse({'success': False, 'message': 'Matrícula ou senha incorretos.'}, status=401)
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Erro interno no servidor.'}, status=500)

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')




@login_required(login_url='login')
def index_view(request):
    # Busca todos os produtos (incluindo os esgotados)
    produtos = Produto.objects.all().order_by('-id')
    
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
                
            compras_ativas = ItemPedido.objects.filter(
                pedido__usuario=request.user,
                produto=produto,
                pedido__descontado_rh=False
            ).exclude(pedido__status='Cancelado').aggregate(Total=Sum('quantidade'))['Total'] or 0
            
            if (compras_ativas + qtd_solicitada) > produto.limite_por_funcionario:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'O limite do produto "{produto.nome}" são {produto.limite_por_funcionario} unidades por ciclo de folha.'
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
            local_retirada = data.get('local_retirada', 'Brasília')
            
            if not itens:
                return JsonResponse({'success': False, 'message': 'O carrinho está vazio.'}, status=400)
                
            # Calcular as compras não baixadas na folha pelo usuário para este produto
            
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
                
                # Buscar quantidade comprada não descontada no RH
                compras_ativas = ItemPedido.objects.filter(
                    pedido__usuario=request.user,
                    produto=produto,
                    pedido__descontado_rh=False
                ).exclude(pedido__status='Cancelado').aggregate(Total=Sum('quantidade'))['Total'] or 0
                
                if (compras_ativas + qtd_solicitada) > produto.limite_por_funcionario:
                    return JsonResponse({
                        'success': False, 
                        'message': f'O limite do produto "{produto.nome}" são {produto.limite_por_funcionario} unidades por ciclo de folha.'
                    }, status=400)
                
                if qtd_solicitada > produto.estoque:
                    return JsonResponse({
                        'success': False, 
                        'message': f'Estoque insuficiente para "{produto.nome}". Temos apenas {produto.estoque} unidades disponíveis.'
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
                termo_aceito=True,
                local_retirada=local_retirada
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
                
                # Atualizar o estoque
                item_val['produto'].estoque -= item_val['quantidade']
                item_val['produto'].save()
                
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
    # Busca os pedidos do usuário, otimizando o carregamento dos itens (N+1 Query Fix)
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-data_pedido').prefetch_related('itens', 'itens__produto')
    return render(request, 'minhas_compras.html', {'pedidos': pedidos})

from django.utils import timezone
from .models import Produto

@login_required(login_url='login')
def painel_admin_view(request):
    if not request.user.is_staff:
        messages.error(request, 'Acesso restrito para administradores.')
        return redirect('index')
    
    produtos = Produto.objects.all().order_by('-id')
    # Prevenção de N+1 garantindo carregamento instantâneo
    pedidos = Pedido.objects.select_related('usuario', 'usuario__profile', 'responsavel_baixa', 'responsavel_retirada').prefetch_related('itens', 'itens__produto').all().order_by('-data_pedido')
    
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
        imagem_cropped_base64 = request.POST.get('imagem_cropped_base64')
        
        if imagem_cropped_base64:
            try:
                format, imgstr = imagem_cropped_base64.split(';base64,') 
                # Blindagem de segurança: forçar JPG (ignora o tipo enviado)
                filename = f"crop_{uuid.uuid4()}.jpg"
                imagem_produto = ContentFile(base64.b64decode(imgstr), name=filename)
            except Exception:
                pass
        
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
            imagem_cropped_base64 = request.POST.get('imagem_cropped_base64')
            
            if imagem_cropped_base64:
                try:
                    format, imgstr = imagem_cropped_base64.split(';base64,') 
                    # Blindagem de segurança: forçar JPG
                    filename = f"crop_{uuid.uuid4()}.jpg"
                    produto.imagem_produto = ContentFile(base64.b64decode(imgstr), name=filename)
                except Exception:
                    pass
            elif imagem_produto:
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
            if pedido.status in ['Pendente', 'Enviado', 'Pronto']:
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

@login_required(login_url='login')
def avancar_status_pedido(request, pedido_id, novo_status):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Não autorizado'}, status=403)
        
    if request.method == 'POST':
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            
            # Validação simples do status
            status_validos = ['Enviado', 'Pronto']
            if novo_status not in status_validos:
                return JsonResponse({'success': False, 'message': 'Status inválido'}, status=400)
                
            pedido.status = novo_status
            pedido.save()
            
            return JsonResponse({'success': True, 'novo_status': novo_status})
        except Pedido.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pedido não encontrado'}, status=404)
            
    return JsonResponse({'success': False, 'message': 'Método inválido'}, status=405)

@login_required(login_url='login')
def imprimir_guia_view(request, pedido_id):
    if not request.user.is_staff:
        messages.error(request, 'Não autorizado')
        return redirect('index')
        
    try:
        pedido = Pedido.objects.select_related('usuario', 'usuario__profile').prefetch_related('itens', 'itens__produto').get(id=pedido_id)
        
        # Só permite imprimir guia para Goiânia, mas não vamos travar o código. 
        # A lógica no template ou no botão vai garantir isso, aqui apenas enviamos os dados.
        return render(request, 'guia_remessa.html', {'pedido': pedido})
    except Pedido.DoesNotExist:
        messages.error(request, 'Pedido não encontrado')
        return redirect('painel_admin')

from django.db.models import Q, F
from django.db.models.functions import TruncMonth
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
    
    pedidos_resumo = Pedido.objects.exclude(status='Cancelado')
    
    if mes:
        pedidos_resumo = pedidos_resumo.filter(data_pedido__month=int(mes))
    if ano:
        pedidos_resumo = pedidos_resumo.filter(data_pedido__year=int(ano))
        
    usuarios = pedidos_resumo.annotate(
        mes_ano=TruncMonth('data_pedido')
    ).values(
        'usuario__id', 
        'usuario__first_name', 
        'usuario__profile__matricula', 
        'usuario__profile__celular', 
        'mes_ano',
        'descontado_rh'
    ).annotate(
        total_gasto=Sum('total')
    ).order_by('-mes_ano', 'descontado_rh', 'usuario__first_name')
    
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
            import json
            data = json.loads(request.body) if request.body else {}
            codigo_ads = data.get('codigo_ads', '').strip()
            
            if not codigo_ads or len(codigo_ads) != 5 or not codigo_ads.isdigit():
                return JsonResponse({'success': False, 'message': 'Código ADS inválido. Deve conter 5 dígitos.'}, status=400)
                
            pedido = Pedido.objects.get(id=pedido_id)
            pedido.descontado_rh = True
            pedido.responsavel_baixa = request.user
            pedido.codigo_ads = codigo_ads
            pedido.save()
            return JsonResponse({
                'success': True, 
                'status': 'baixado',
                'responsavel': request.user.first_name or request.user.username,
                'codigo_ads': codigo_ads
            })
        except Pedido.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pedido não encontrado'}, status=404)
            
    return JsonResponse({'success': False, 'message': 'Método inválido'}, status=405)
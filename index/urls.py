from django.urls import path
from . import views


urlpatterns = [
    path('', views.index_view, name='index'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('buscar-colaborador/', views.buscar_colaborador, name='buscar_colaborador'),
    path('recuperar-senha/', views.recuperar_senha_view, name='recuperar_senha'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('verificar-codigo/', views.verificar_codigo_view, name='verificar_codigo'),
    path('reenviar-codigo/', views.reenviar_codigo_view, name='reenviar_codigo'),
    path('nova-senha/<uidb64>/<token>/', views.nova_senha_view, name='nova_senha'),
    path('verificar-limite/', views.verificar_limite_view, name='verificar_limite'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('comprovante/<int:pedido_id>/', views.comprovante_view, name='comprovante'),
    path('minhas-compras/', views.minhas_compras_view, name='minhas_compras'),
    path('painel-admin/', views.painel_admin_view, name='painel_admin'),
    path('relatorio-rh/', views.relatorio_rh_view, name='relatorio_rh'),
    path('relatorio-rh/funcionario/<int:user_id>/', views.relatorio_rh_detalhes_view, name='relatorio_rh_detalhes'),
    path('relatorio-rh/dar-baixa/<int:pedido_id>/', views.dar_baixa_rh_view, name='dar_baixa_rh'),
    path('adicionar-produto/', views.adicionar_produto, name='adicionar_produto'),
    path('deletar-produto/<int:produto_id>/', views.deletar_produto, name='deletar_produto'),
    path('editar-produto/<int:produto_id>/', views.editar_produto, name='editar_produto'),
    path('dar-baixa-pedido/<int:pedido_id>/', views.dar_baixa_pedido, name='dar_baixa_pedido'),
]
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index_view, name='index'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('recuperar-senha/', views.recuperar_senha_view, name='recuperar_senha'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('verificar-codigo/', views.verificar_codigo_view, name='verificar_codigo'),
    path('reenviar-codigo/', views.reenviar_codigo_view, name='reenviar_codigo'),
    path('nova-senha/<uidb64>/<token>/', views.nova_senha_view, name='nova_senha'),
]
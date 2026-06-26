from django.contrib import admin

from .models import Colaborador, UserProfile, Pedido, ItemPedido, Produto

@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'nome', 'email')
    search_fields = ('matricula', 'nome', 'email')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'matricula', 'celular')
    search_fields = ('user__email', 'user__first_name', 'matricula', 'celular')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'avaria', 'preco_desconto', 'estoque')
    search_fields = ('nome', 'avaria')
    list_filter = ('avaria',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'status', 'total', 'data_pedido', 'data_retirada')
    list_filter = ('status', 'data_pedido', 'data_retirada')
    search_fields = ('usuario__first_name', 'usuario__email')

admin.site.register(ItemPedido)

from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import Colaborador, UserProfile, Pedido, ItemPedido, Produto

@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'nome')
    search_fields = ('matricula', 'nome')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'matricula', 'celular')
    search_fields = ('user__first_name', 'matricula', 'celular')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'avaria', 'preco_desconto', 'estoque')
    search_fields = ('nome', 'avaria')
    list_filter = ('avaria',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'status', 'total', 'descontado_rh', 'data_pedido', 'data_retirada')
    list_filter = ('status', 'descontado_rh', 'data_pedido', 'data_retirada')
    search_fields = ('usuario__first_name',)
    actions = ['marcar_como_descontado']

    @admin.action(description='Marcar pedidos selecionados como Descontados na Folha (Libera limite)')
    def marcar_como_descontado(self, request, queryset):
        if 'apply' in request.POST:
            codigo_ads = request.POST.get('codigo_ads', '').strip()
            if not codigo_ads or len(codigo_ads) != 5 or not codigo_ads.isdigit():
                self.message_user(request, "Ação cancelada: O código ADS deve conter exatamente 5 dígitos numéricos.", level=messages.ERROR)
                return HttpResponseRedirect(request.get_full_path())
            
            # Atualiza os pedidos para descontado_rh=True, guarda quem fez a baixa e o código ADS
            count = queryset.update(descontado_rh=True, responsavel_baixa=request.user, codigo_ads=codigo_ads)
            self.message_user(request, f"{count} pedido(s) marcados como descontados na folha com o Código ADS {codigo_ads}.")
            return HttpResponseRedirect(request.get_full_path())
            
        context = {
            'queryset': queryset,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        }
        return render(request, 'admin/pedido_marcar_descontado.html', context)

admin.site.register(ItemPedido)

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

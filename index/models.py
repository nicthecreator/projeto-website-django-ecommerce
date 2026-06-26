from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

from django.contrib.auth.models import User as AuthUser

class Colaborador(models.Model):
    matricula = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True, blank=True, null=True)
    
    def __str__(self):
        return f"{self.matricula} - {self.nome}"

class UserProfile(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, related_name='profile')
    matricula = models.CharField(max_length=20, unique=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    is_rh = models.BooleanField(default=False, help_text="Designa se este usuário tem acesso ao Relatório do RH.")
    
    def __str__(self):
        return f"Perfil de {self.user.first_name}"

class Produto(models.Model):
    nome = models.CharField(max_length=200)
    avaria = models.CharField(max_length=200)
    preco_original = models.DecimalField(max_digits=10, decimal_places=2)
    preco_desconto = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)
    limite_por_funcionario = models.PositiveIntegerField(default=1, help_text="Limite de compras a cada 24 horas por funcionário.")
    imagem_produto = models.ImageField(upload_to='produtos/', blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.avaria}"

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente (Aguardando Retirada)'),
        ('Retirado', 'Retirado (Finalizado)'),
        ('Cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='pedidos')
    data_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    desconto_folha = models.BooleanField(default=True)
    descontado_rh = models.BooleanField(default=False, help_text="Verdadeiro se o RH já deu baixa na folha de pagamento.")
    responsavel_baixa = models.ForeignKey(AuthUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='baixas_realizadas')
    termo_aceito = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendente')
    data_retirada = models.DateTimeField(blank=True, null=True)
    responsavel_retirada = models.ForeignKey(AuthUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='retiradas_realizadas')
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.first_name} - {self.status}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True, blank=True)
    produto_nome = models.CharField(max_length=200)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def get_subtotal(self):
        return self.quantidade * self.preco_unitario

    def __str__(self):
        return f"{self.quantidade}x {self.produto_nome}"


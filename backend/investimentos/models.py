from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum

class Instituicao(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    # Ex: Banco do Brasil, XP Investimentos, Nubank
    
    def __str__(self):
        return self.nome

class Conta(models.Model):
    TIPO_CONTA = [
        ('CORRENTE', 'Conta Corrente'),
        ('INVESTIMENTO', 'Conta Investimento/Corretora'),
        ('POUPANCA', 'Poupança'),
    ]
    
    nome = models.CharField(max_length=50)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CONTA)
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_atual = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    

    def __str__(self):
        return f"{self.nome} ({self.instituicao.nome})"

class TipoAtivo(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome

class Ativo(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    nome_empresa = models.CharField(max_length=100)
    tipo = models.ForeignKey(TipoAtivo, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.ticker} - {self.nome_empresa}"

class Lancamento(models.Model):
    TIPO_OPERACAO = [
        ('C', 'Compra'),
        ('V', 'Venda'),
        ('D', 'Dividendo/JCP'), # Adicionado para controle de renda
    ]

    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE)
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='lancamentos')
    data = models.DateField()
    quantidade = models.DecimalField(max_digits=12, decimal_places=4)
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    taxas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tipo_operacao = models.CharField(max_length=1, choices=TIPO_OPERACAO)

    @property
    def valor_total(self):
        # Na compra, você gasta (preço + taxas). Na venda, você recebe (preço - taxas).
        if self.tipo_operacao == 'C':
            return (self.quantidade * self.preco_unitario) + self.taxas
        return (self.quantidade * self.preco_unitario) - self.taxas

    def __str__(self):
        return f"{self.get_tipo_operacao_display()} - {self.ativo.ticker}"

class MovimentacaoConta(models.Model):
    TIPO_MOV = [
        ('E', 'Entrada (Depósito)'),
        ('S', 'Saída (Saque/Pagamento)'),
    ]
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    data = models.DateField()
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    descricao = models.CharField(max_length=100)
    tipo = models.CharField(max_length=1, choices=TIPO_MOV)

    def __str__(self):
        return f"{self.tipo} - {self.valor} em {self.conta}"
        
        
@receiver([post_save, post_delete], sender=Lancamento)
@receiver([post_save, post_delete], sender=MovimentacaoConta)
def atualizar_saldo_conta(sender, instance, **kwargs):
    """
    Sinal que dispara sempre que um Lançamento ou Movimentação 
    for criado, editado ou deletado.
    """
    conta = instance.conta
    
    # 1. Soma Entradas de Movimentação (Depósitos)
    entradas_mov = MovimentacaoConta.objects.filter(
        conta=conta, tipo='E'
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # 2. Soma Saídas de Movimentação (Saques)
    saidas_mov = MovimentacaoConta.objects.filter(
        conta=conta, tipo='S'
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # 3. Soma Vendas de Ativos (Entra dinheiro na conta)
    vendas = Lancamento.objects.filter(
        conta=conta, tipo_operacao='V'
    )
    total_vendas = sum(l.valor_total for l in vendas)
    
    # 4. Soma Compras de Ativos (Sai dinheiro da conta)
    compras = Lancamento.objects.filter(
        conta=conta, tipo_operacao='C'
    )
    total_compras = sum(l.valor_total for l in compras)

    # 5. Soma Dividendos (Entra dinheiro na conta)
    dividendos = Lancamento.objects.filter(
        conta=conta, tipo_operacao='D'
    ).aggregate(total=Sum('preco_unitario'))['total'] or 0 # Simplificado

    # Cálculo Final
    conta.saldo_atual = (
        conta.saldo_inicial + 
        entradas_mov + 
        total_vendas + 
        dividendos - 
        saidas_mov - 
        total_compras
    )
    
    # Usamos update para evitar disparar o signal da própria conta em loop
    Conta.objects.filter(pk=conta.pk).update(saldo_atual=conta.saldo_atual)

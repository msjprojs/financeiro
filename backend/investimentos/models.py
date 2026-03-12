from django.db import models, transaction
from django.db.models import Sum, F, Q, Case, When, Value, DecimalField
from django.db.models.functions import Coalesce

class Instituicao(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.nome

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
    # editable=False pois será controlado apenas via lógica interna
    saldo_atual = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)

    def __str__(self):
        return f"{self.nome} ({self.instituicao.nome})"

    def atualizar_saldo_cache(self):
        """
        Recalcula o saldo total do zero para corrigir eventuais divergências.
        Útil para auditoria ou correção manual.
        """
        # Movimentações simples
        movs = MovimentacaoConta.objects.filter(conta=self).aggregate(
            entradas=Coalesce(Sum('valor', filter=Q(tipo='E')), Value(0), output_field=DecimalField()),
            saidas=Coalesce(Sum('valor', filter=Q(tipo='S')), Value(0), output_field=DecimalField()),
        )
        
        # Transferências
        trans_in = Transferencia.objects.filter(conta_destino=self).aggregate(t=Sum('valor'))['t'] or 0
        trans_out = Transferencia.objects.filter(conta_origem=self).aggregate(t=Sum('valor'))['t'] or 0
        
        # Ativos (Lógica SQL pura para performance)
        ativos = Lancamento.objects.filter(conta=self).aggregate(
            compras=Coalesce(Sum(F('quantidade') * F('preco_unitario') + F('taxas'), filter=Q(tipo_operacao='C')), Value(0), output_field=DecimalField()),
            vendas=Coalesce(Sum(F('quantidade') * F('preco_unitario') - F('taxas'), filter=Q(tipo_operacao='V')), Value(0), output_field=DecimalField()),
            dividendos=Coalesce(Sum('preco_unitario', filter=Q(tipo_operacao='D')), Value(0), output_field=DecimalField()),
        )

        novo_saldo = (
            self.saldo_inicial + 
            movs['entradas'] - movs['saidas'] + 
            trans_in - trans_out + 
            ativos['vendas'] + ativos['dividendos'] - ativos['compras']
        )
        
        self.saldo_atual = novo_saldo
        self.save(update_fields=['saldo_atual'])

# --- Modelos de Movimentação ---

class MovimentacaoConta(models.Model):
    TIPO_MOV = [('E', 'Entrada'), ('S', 'Saída')]
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    tipo = models.CharField(max_length=1, choices=TIPO_MOV)
    data = models.DateField()

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            delta = self.valor if self.tipo == 'E' else -self.valor
            Conta.objects.filter(pk=self.conta_id).update(saldo_atual=F('saldo_atual') + delta)

class Transferencia(models.Model):
    conta_origem = models.ForeignKey(Conta, related_name='transf_enviadas', on_delete=models.CASCADE)
    conta_destino = models.ForeignKey(Conta, related_name='transf_recebidas', on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateField()

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk: # Se for edição, idealmente você deve estornar o anterior (lógica omitida por brevidade)
                pass
            super().save(*args, **kwargs)
            Conta.objects.filter(pk=self.conta_origem_id).update(saldo_atual=F('saldo_atual') - self.valor)
            Conta.objects.filter(pk=self.conta_destino_id).update(saldo_atual=F('saldo_atual') + self.valor)

# --- Ativos ---

class TipoAtivo(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome

class Ativo(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    nome_empresa = models.CharField(max_length=100)
    tipo = models.ForeignKey('TipoAtivo', on_delete=models.PROTECT)

    def __str__(self):
        return self.ticker

class Lancamento(models.Model):
    TIPO_OPERACAO = [('C', 'Compra'), ('V', 'Venda'), ('D', 'Dividendo')]
    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE)
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    quantidade = models.DecimalField(max_digits=12, decimal_places=4)
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    taxas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tipo_operacao = models.CharField(max_length=1, choices=TIPO_OPERACAO)
    data = models.DateField()

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            # Cálculo do impacto financeiro na conta
            if self.tipo_operacao == 'C':
                valor_final = -( (self.quantidade * self.preco_unitario) + self.taxas )
            elif self.tipo_operacao == 'V':
                valor_final = (self.quantidade * self.preco_unitario) - self.taxas
            else: # Dividendo
                valor_final = self.preco_unitario 
            
            Conta.objects.filter(pk=self.conta_id).update(saldo_atual=F('saldo_atual') + valor_final)

    def __str__(self):
        #return f"{self.ativo} - {self.conta}"
        return f"{self.ativo.ticker} {self.tipo_operacao} {self.quantidade} em {self.data}"


class TransacaoFinanceira(models.Model):
    # Identificadores
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='fluxo')
    data = models.DateField()
    valor = models.DecimalField(max_digits=12, decimal_places=2) # Positivo (entrada) ou Negativo (saída)
    descricao = models.CharField(max_length=255)
    
    # Links para a origem (Generic Foreign Key ou campos simples)
    # Aqui usamos campos simples para facilitar o entendimento
    origem_mov = models.ForeignKey(MovimentacaoConta, on_delete=models.CASCADE, null=True, blank=True)
    origem_transf = models.ForeignKey(Transferencia, on_delete=models.CASCADE, null=True, blank=True)
    origem_lanc = models.ForeignKey(Lancamento, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['data', 'id']
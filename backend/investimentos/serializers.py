from rest_framework import serializers

from .models import Ativo, Conta, Instituicao, Lancamento, MovimentacaoConta, TipoAtivo, Transferencia, TransacaoFinanceira


class InstituicaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instituicao
        fields = "__all__"


class ContaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conta
        fields = "__all__"


class TipoAtivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAtivo
        fields = "__all__"


class AtivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ativo
        fields = "__all__"


class LancamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lancamento
        fields = "__all__"


class MovimentacaoContaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimentacaoConta
        fields = "__all__"


class TransferenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transferencia
        fields = "__all__"


class TransacaoFinanceiraSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransacaoFinanceira
        fields = "__all__"

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Ativo, Conta, Instituicao, Lancamento, MovimentacaoConta, TipoAtivo, Transferencia, TransacaoFinanceira
from .serializers import AtivoSerializer, ContaSerializer, InstituicaoSerializer, LancamentoSerializer, MovimentacaoContaSerializer, TipoAtivoSerializer, TransferenciaSerializer, TransacaoFinanceiraSerializer



class InstituicaoViewSet(viewsets.ModelViewSet):
    queryset = Instituicao.objects.all()
    serializer_class = InstituicaoSerializer

class ContaViewSet(viewsets.ModelViewSet):
    queryset = Conta.objects.all()
    serializer_class = ContaSerializer

class TipoAtivoViewSet(viewsets.ModelViewSet):
    queryset = TipoAtivo.objects.all()
    serializer_class = TipoAtivoSerializer

class AtivoViewSet(viewsets.ModelViewSet):
    queryset = Ativo.objects.all()
    serializer_class = AtivoSerializer  

class LancamentoViewSet(viewsets.ModelViewSet):
    queryset = Lancamento.objects.all()
    serializer_class = LancamentoSerializer 

class MovimentacaoContaViewSet(viewsets.ModelViewSet):
    queryset = MovimentacaoConta.objects.all()
    serializer_class = MovimentacaoContaSerializer

class TransferenciaViewSet(viewsets.ModelViewSet):
    queryset = Transferencia.objects.all()
    serializer_class = TransferenciaSerializer

class TransferenciaFinanceiraViewSet(viewsets.ModelViewSet):
    queryset = TransacaoFinanceira.objects.all()
    serializer_class = TransacaoFinanceiraSerializer
    
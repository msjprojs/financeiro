import os
import django
import json
from decimal import Decimal

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from investimentos.models import TipoAtivo, Ativo, Lancamento, Instituicao, Conta, MovimentacaoConta, TransacaoFinanceira, Transferencia


def exportar():
    dados = {
        'tipos': list(TipoAtivo.objects.values('id', 'nome')),
        'ativos': list(Ativo.objects.values('id', 'ticker', 'nome_empresa', 'tipo_id')),
        'instituicoes': list(Instituicao.objects.values('id', 'nome')),
        'contas': [],
        'lancamentos': [],
        'movimentacoesconta': [],
        'transacaofinanceira': [],
        'transferencia': []
    }

    # Contas possuem Decimais, que o JSON nativo não aceita. 
    # Precisamos converter para string.
    for c in Conta.objects.all():
        dados['contas'].append({
            'id': c.id,
            'nome': c.nome,
            'instituicao': c.instituicao_id,
            'tipo': c.tipo,
            'saldo_inicial': str(c.saldo_inicial),
            'saldo_atual': str(c.saldo_atual)
        })

    # Lancamentos possuem Decimais e Datas, que o JSON nativo não aceita. 
    # Precisamos converter para string.
    for d in Lancamento.objects.all():
        dados['lancamentos'].append({
            'ativo_id': d.ativo_id,
            'conta_id': d.conta_id,
            'data': str(d.data),
            'quantidade': str(d.quantidade),
            'preco_unitario': str(d.preco_unitario),
            'taxas': str(d.taxas),
            'tipo_operacao': d.tipo_operacao
        })

    for m in MovimentacaoConta.objects.all():   
        dados['movimentacoesconta'].append({
            'conta_id': m.conta_id,
            'data': str(m.data),
            'valor': str(m.valor),
            'tipo': m.tipo
        })

    for t in TransacaoFinanceira.objects.all():
        dados['transacaofinanceira'].append({
            'conta_id': t.conta_id,
            'valor': str(t.valor),
            'data': str(t.data),
            'descricao': t.descricao
        })

    for f in Transferencia.objects.all():
        dados['transferencia'].append({
            'conta_origem_id': f.conta_origem_id,
            'conta_destino_id': f.conta_destino_id,
            'valor': str(f.valor),
            'data': str(f.data)
        })

    with open('backup_investimentos.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    
    print("✅ Dados exportados com sucesso para backup_investimentos.json")

if __name__ == "__main__":
    exportar()

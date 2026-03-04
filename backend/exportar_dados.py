import os
import django
import json
from decimal import Decimal

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from investimentos.models import TipoAtivo, Ativo, Lancamento, Instituicao, Conta


def exportar():
    dados = {
        'tipos': list(TipoAtivo.objects.values('id', 'nome')),
        'ativos': list(Ativo.objects.values('id', 'ticker', 'nome_empresa', 'tipo_id')),
        'instituicoes': list(Instituicao.objects.values('id', 'nome')),
        'contas': [],
        'lancamentos': []
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
    for l in Lancamento.objects.all():
        dados['lancamentos'].append({
            'ativo_id': l.ativo_id,
            'data': str(l.data),
            'quantidade': str(l.quantidade),
            'preco_unitario': str(l.preco_unitario),
            'taxas': str(l.taxas),
            'tipo_operacao': l.tipo_operacao
        })

    with open('backup_investimentos.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    
    print("✅ Dados exportados com sucesso para backup_investimentos.json")

if __name__ == "__main__":
    exportar()

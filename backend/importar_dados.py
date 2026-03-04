import os
import django
import json
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from investimentos.models import TipoAtivo, Ativo, Lancamento

def importar():
    if not os.path.exists('backup_investimentos.json'):
        print("❌ Arquivo de backup não encontrado!")
        return

    with open('backup_investimentos.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)

    print("Iniciando importação...")

    # 1. Importar Tipos de Ativos
    for t in dados['tipos']:
        TipoAtivo.objects.get_or_create(id=t['id'], defaults={'nome': t['nome']})

    # 2. Importar Ativos
    for a in dados['ativos']:
        Ativo.objects.get_or_create(
            id=a['id'], 
            defaults={
                'ticker': a['ticker'], 
                'nome_empresa': a['nome_empresa'], 
                'tipo_id': a['tipo_id']
            }
        )

    # 3. Importar Lançamentos
    for l in dados['lancamentos']:
        Lancamento.objects.create(
            ativo_id=l['ativo_id'],
            data=l['data'],
            quantidade=Decimal(l['quantidade']),
            preco_unitario=Decimal(l['preco_unitario']),
            taxas=Decimal(l['taxas']),
            tipo_operacao=l['tipo_operacao']
        )

    print("🚀 Importação concluída com sucesso!")

if __name__ == "__main__":
    importar()

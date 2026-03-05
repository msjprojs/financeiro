from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from .models import MovimentacaoConta, Transferencia, TransacaoFinanceira


@receiver(post_save, sender=MovimentacaoConta)
def sync_movimentacao(sender, instance, **kwargs):
    valor_final = instance.valor if instance.tipo == 'E' else -instance.valor
    TransacaoFinanceira.objects.update_or_create(
        origem_mov=instance,
        defaults={
            'conta': instance.conta,
            'data': instance.data,
            'valor': valor_final,
            'descricao': f"Movimentação: {instance.descricao}"
        }
    )

@receiver(post_save, sender=Transferencia)
def sync_transferencia(sender, instance, **kwargs):
    # Uma transferência gera DUAS entradas no fluxo: uma saída e uma entrada
    # Saída da origem
    TransacaoFinanceira.objects.update_or_create(
        origem_transf=instance,
        valor__lt=0, # Filtro para identificar a perna de saída
        defaults={
            'conta': instance.conta_origem,
            'data': instance.data,
            'valor': -instance.valor,
            'descricao': f"Transf. para {instance.conta_destino}"
        }
    )
    # Entrada no destino
    TransacaoFinanceira.objects.update_or_create(
        origem_transf=instance,
        valor__gt=0, # Filtro para identificar a perna de entrada
        defaults={
            'conta': instance.conta_destino,
            'data': instance.data,
            'valor': instance.valor,
            'descricao': f"Transf. de {instance.conta_origem}"
        }
    )
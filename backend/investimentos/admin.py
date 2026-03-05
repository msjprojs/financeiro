from django.contrib import admin

from .models import Ativo, Conta, Instituicao, Lancamento, MovimentacaoConta, TipoAtivo, Transferencia

admin.site.register(Instituicao)
admin.site.register(Conta)
admin.site.register(TipoAtivo)
admin.site.register(Ativo)
admin.site.register(Lancamento)
admin.site.register(MovimentacaoConta)
admin.site.register(Transferencia)

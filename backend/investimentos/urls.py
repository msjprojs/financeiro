from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import InstituicaoViewSet, ContaViewSet, TipoAtivoViewSet, AtivoViewSet, LancamentoViewSet, MovimentacaoContaViewSet


router = DefaultRouter()
router.register(r'instituicao', InstituicaoViewSet, basename='instituicao')
router.register(r'conta', ContaViewSet, basename='conta')   
router.register(r'tipoativo', TipoAtivoViewSet, basename='tipoativo')   
router.register(r'ativo', AtivoViewSet, basename='ativo')   
router.register(r'lancamento', LancamentoViewSet, basename='lancamento')   
router.register(r'movimentacaoconta', MovimentacaoContaViewSet, basename='movimentacaoconta')   
                
urlpatterns = [
    path('', include(router.urls)),
]

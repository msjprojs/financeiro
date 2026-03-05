from django.apps import AppConfig


class InvestimentosConfig(AppConfig):
    name = 'investimentos'

    def ready(self):
        # Isso garante que os signals sejam registrados quando o servidor subir
        import investimentos.signals
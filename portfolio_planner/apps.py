from django.apps import AppConfig


class PortfolioPlannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portfolio_planner'
    verbose_name = 'Portfolio Planner'

    def ready(self):
        # Ensure signals are wired up
        import portfolio_planner.signals

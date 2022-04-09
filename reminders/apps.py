from threading import Thread
from django.apps import AppConfig


class RemindersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reminders'

    scheduler = None

    def ready(self) -> None:
        print("ready")

        if self.scheduler is None:
            Thread(target=RemindersConfig.create_scheduler, daemon=True).start()

    @staticmethod
    def create_scheduler():
        from reminders.scheduler import UserAlertScheduler
        RemindersConfig.scheduler = UserAlertScheduler()

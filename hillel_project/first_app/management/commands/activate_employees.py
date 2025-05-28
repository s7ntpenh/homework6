from django.core.management.base import BaseCommand
from first_app.models import Employee

class Command(BaseCommand):
    help = 'Активує всіх працівників (is_active=True)'

    def handle(self, *args, **kwargs):
        updated_count = Employee.objects.update(is_active=True)

        self.stdout.write(
            self.style.SUCCESS(f'Успішно активовано {updated_count} працівників.')
        )
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Sample management command for the report app.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Successfully ran command for report!'))

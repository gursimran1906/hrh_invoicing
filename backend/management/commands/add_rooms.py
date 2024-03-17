
from django.core.management.base import BaseCommand
from backend.models import Room 

class Command(BaseCommand):
    help = 'Add shared rooms to the database'

    def add_arguments(self, parser):
        parser.add_argument('num_rooms', type=int, help='Number of rooms to add')

    def handle(self, *args, **options):
        num_rooms = options['num_rooms']
        
        for i in range(1,43):
            
            room, created = Room.objects.get_or_create(id=i)

            if created:
                self.stdout.write(self.style.SUCCESS(f"Shared room  added successfully."))
            else:
                self.stdout.write(self.style.WARNING(f"Shared room  already exists."))

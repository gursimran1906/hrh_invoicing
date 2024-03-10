
from django.core.management.base import BaseCommand
from backend.models import Room 

class Command(BaseCommand):
    help = 'Add shared rooms to the database'

    def handle(self, *args, **options):
        shared_room_numbers = [1, 2, 16, 17]

        for i in range(1,43):
            if i in shared_room_numbers:
                room, created = Room.objects.get_or_create(id=i, is_shared=True)
            else:
                room, created = Room.objects.get_or_create(id=i)

            if created:
                self.stdout.write(self.style.SUCCESS(f"Shared room  added successfully."))
            else:
                self.stdout.write(self.style.WARNING(f"Shared room  already exists."))

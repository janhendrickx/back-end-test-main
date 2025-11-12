from django.core.management.base import BaseCommand
# Enable atomic transactions
from django.db import transaction
from ...models import Vessel
import threading


class Command(BaseCommand):
    help = "Simulate condition when withdrawing refrigerant from a vessel."

    def handle(self, *args, **kwargs):
        Vessel.objects.create(name="Test Vessel", content=50.0)
        self.stdout.write("Simulating condition...")
        self.run_simulation()

    def run_simulation(self):
        barrier = threading.Barrier(2)

        def user1():
            barrier.wait()
            # Wrap the atomic transaction
            with transaction.atomic():
                # Lock the row to prevent race conditions during concurrent updates
                vessel = Vessel.objects.select_for_update().get(id=1)
                vessel.content -= 10.0
                vessel.save()

        def user2():
            barrier.wait()
            # Wrap the atomic transaction
            with transaction.atomic():
                # Lock the row to prevent race conditions during concurrent updates
                vessel = Vessel.objects.select_for_update().get(id=1)
                vessel.content -= 10.0
                vessel.save()

        t1 = threading.Thread(target=user1)
        t2 = threading.Thread(target=user2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        vessel = Vessel.objects.get(id=1)
        self.stdout.write(f"Remaining content: {vessel.content} kg")

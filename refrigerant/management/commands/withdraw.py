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
        results = []  # Collect output messages

        def withdraw(user_id):
            # Wrap the atomic transaction
            with transaction.atomic():
                # Lock the row to prevent race conditions during concurrent updates
                vessel = Vessel.objects.select_for_update().get(id=1)
                if vessel.content >= 10.0:
                    vessel.content -= 10.0
                    vessel.save()
                    return f"User {user_id}: Withdrawal successful."
                else:
                    return f"User {user_id}: Withdrawal failed — insufficient content."

        def user1():
            barrier.wait()
            result = withdraw(1)
            results.append(result)

        def user2():
            barrier.wait()
            result = withdraw(2)
            results.append(result)

        t1 = threading.Thread(target=user1)
        t2 = threading.Thread(target=user2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Print results from both threads
        for message in results:
            print(message)

        # Show final vessel content
        vessel = Vessel.objects.get(id=1)
        self.stdout.write(f"Remaining content: {vessel.content} kg")
        

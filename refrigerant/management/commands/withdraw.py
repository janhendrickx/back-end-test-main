from django.core.management.base import BaseCommand
# Enable atomic transactions
from django.db import transaction
from ...models import Vessel
import threading
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
MAX_WITHDRAWAL = float(os.getenv("MAX_WITHDRAWAL", 10.0))
VESSEL_ID = int(os.getenv("VESSEL_ID", 1))


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
                if vessel.content >= MAX_WITHDRAWAL:
                    vessel.content -= MAX_WITHDRAWAL
                    vessel.save()
                    return f"User {user_id}: Withdrawal successful."
                else:
                    if vessel.content > MAX_WITHDRAWAL:
                        return f"User {user_id}: Withdrawal failed — only {vessel.content} kg available."
                    elif vessel.content == 0:
                        return f"User {user_id}: Withdrawal failed — Insufficient content"
                        

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
        if vessel.content < 1:
            self.stdout.write(f"No more content remaining")
        else:
            self.stdout.write(f"Remaining content: {vessel.content} kg")
        

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

        def user_thread(user_id):
            barrier.wait()
            try:
                vessel = Vessel.objects.get(id=VESSEL_ID)
                success, message = vessel.withdraw(MAX_WITHDRAWAL)
            except Exception as e:
                message = f"Error during withdrawal: {str(e)}"
            results.append(f"User {user_id}: {message}")

        t1 = threading.Thread(target=lambda: user_thread(1))
        t2 = threading.Thread(target=lambda: user_thread(2))
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
        

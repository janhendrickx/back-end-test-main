from django.db import models, transaction


class Vessel(models.Model):
    name = models.CharField(max_length=100)
    content = models.PositiveIntegerField()

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")

        with transaction.atomic():
            # Lock the row to prevent concurrent modification
            vessel = Vessel.objects.select_for_update().get(id=self.id)

            if vessel.content >= amount:
                vessel.content -= amount
                vessel.save()
                return True, f"Withdrawal of {amount} kg successful."
            else:
                if vessel.content > amount:
                    return False, f"Withdrawal failed — only {vessel.content} kg available."
                elif vessel.content == 0:
                    return False, f"Withdrawal failed — No more vessel content available."

    def clean(self):
        if self.content < 0:
            raise ValidationError("Vessel content cannot be negative.")

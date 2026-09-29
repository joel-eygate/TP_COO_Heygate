from django.test import TestCase

from .models import Machine


class MachineModelTests(TestCase):
    def test_machine_creation(self):
        self.assertEqual(Machine.objects.count(), 0)
        Machine.objects.create(
            nom="CNC", prix=28_000, duree_de_vie=1, cout_maintenance=1, superficie=1000
        )
        self.assertEqual(Machine.objects.count(), 1)

from django.test import TestCase
from core.models import Wilaya

class WilayaModelTest(TestCase):
    def setUp(self):
        self.wilaya = Wilaya.objects.create(
            code="16",
            name="Alger",
            home_delivery_price=600.00,
            bureau_delivery_price=400.00
        )

    def test_wilaya_creation(self):
        self.assertEqual(self.wilaya.code, "16")
        self.assertEqual(self.wilaya.name, "Alger")
        
    def test_wilaya_str(self):
        self.assertEqual(str(self.wilaya), "16 - Alger")

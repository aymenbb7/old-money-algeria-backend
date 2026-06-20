from django.test import TestCase
from products.models import Product, Collection

class ProductModelTest(TestCase):
    def setUp(self):
        self.collection = Collection.objects.create(name="Summer Essentials")
        self.product = Product.objects.create(
            name="Classic White Polo",
            description="Premium cotton polo.",
            price=4500.00,
            sku="POLO-WHT-001"
        )
        self.product.collections.add(self.collection)

    def test_product_slug_generation(self):
        self.assertEqual(self.product.slug, "classic-white-polo")

    def test_product_str(self):
        self.assertEqual(str(self.product), "Classic White Polo")

    def test_collection_str(self):
        self.assertEqual(str(self.collection), "Summer Essentials")

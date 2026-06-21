from django.core.management.base import BaseCommand
from core.models import HomepageSection
from products.models import Product

class Command(BaseCommand):
    help = 'Seeds initial homepage sections'

    def handle(self, *args, **kwargs):
        sections_data = [
            {'title': 'Nouveautés', 'type': 'NOUVEAUTES', 'order': 1},
            {'title': 'Les Plus Vendus', 'type': 'BESTSELLERS', 'order': 2},
            {'title': 'Nos Recommandations', 'type': 'RECOMMANDATIONS', 'order': 3},
        ]

        products = list(Product.objects.filter(status='PUBLISHED')[:10])

        for data in sections_data:
            section, created = HomepageSection.objects.get_or_create(
                section_type=data['type'],
                defaults={
                    'title': data['title'],
                    'display_order': data['order'],
                    'is_active': True
                }
            )
            
            # If products exist and section was just created (or we want to ensure it has something),
            # we assign some products. For simplicity, assign first 5 to Nouveautés, etc.
            # But the requirement says: "The seed command must assign products only if published products exist. If no products exist, create sections without products (no crash)."
            
            if products and not section.products.exists():
                section.products.set(products[:5])
                
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created section: {data['title']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Section already exists: {data['title']}"))
                
        self.stdout.write(self.style.SUCCESS("Successfully seeded homepage sections."))

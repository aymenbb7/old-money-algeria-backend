from django.core.management.base import BaseCommand
from core.models import LookbookItem
import requests
from django.core.files.base import ContentFile
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Seeds lookbook items'

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting existing LookbookItems...")
        LookbookItem.objects.all().delete()
        
        items = [
            {
                'title': "Le Style Algérien Moderne",
                'description': "Découvrez une collection qui marie l'élégance intemporelle à la modernité algérienne. Chaque pièce est conçue pour affirmer votre présence avec subtilité.",
                'url': 'https://images.unsplash.com/photo-1617137968427-85924c800a22?w=1920&q=80',
                'collection_slug': 'essentiels',
                'order': 1
            },
            {
                'title': "L'Élégance du Quotidien",
                'description': "Des coupes minimalistes, des matières nobles et un confort absolu. Adoptez une garde-robe qui reflète votre goût pour le luxe discret tous les jours.",
                'url': 'https://images.unsplash.com/photo-1516257984-b1b4d707412e?w=1920&q=80',
                'collection_slug': 'chemises',
                'order': 2
            },
            {
                'title': "Old Money Essentials",
                'description': "L'essence même du style 'Old Money'. Des nuances neutres, des silhouettes épurées et une qualité irréprochable pour une allure sophistiquée.",
                'url': 'https://images.unsplash.com/photo-1598808503746-f34cfab8a0c0?w=1920&q=80',
                'collection_slug': 'polos',
                'order': 3
            }
        ]

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

        for item_data in items:
            self.stdout.write(f"Downloading image for {item_data['title']}...")
            try:
                response = requests.get(item_data['url'], headers=headers, timeout=15)
                response.raise_for_status()
                file_name = slugify(item_data['title']) + '.jpg'
                
                item = LookbookItem(
                    title=item_data['title'],
                    description=item_data['description'],
                    collection_slug=item_data['collection_slug'],
                    order=item_data['order']
                )
                item.image.save(file_name, ContentFile(response.content), save=True)
                self.stdout.write(self.style.SUCCESS(f"Successfully created {item.title}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create {item_data['title']}: {e}"))
                self.stdout.write("Falling back to a generic elegant placeholder image...")
                fallback_url = "https://images.unsplash.com/photo-1490114538077-0a7f8cb49891?w=1920&q=80"
                try:
                    res = requests.get(fallback_url, headers=headers, timeout=15)
                    item = LookbookItem(
                        title=item_data['title'],
                        description=item_data['description'],
                        collection_slug=item_data['collection_slug'],
                        order=item_data['order']
                    )
                    item.image.save(slugify(item_data['title']) + '_fallback.jpg', ContentFile(res.content), save=True)
                    self.stdout.write(self.style.SUCCESS(f"Successfully created {item.title} with fallback image"))
                except Exception as fallback_err:
                    self.stdout.write(self.style.ERROR(f"Fallback also failed: {fallback_err}"))

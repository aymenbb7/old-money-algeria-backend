import os
from django.core.management.base import BaseCommand
from orders.models import Order
from products.models import Product, Collection, ProductImage, ProductVariant
from core.models import HomepageSection, StoreSettings

class Command(BaseCommand):
    help = 'Seeds demo data for the Old Money Algeria project'

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting all test data...')
        Order.objects.all().delete()
        Product.objects.all().delete()
        Collection.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All test data deleted.'))

        self.stdout.write('Creating 3 real collections...')
        c1 = Collection.objects.create(
            name="Chemises Premium",
            slug="chemises-premium",
            description="Des chemises élégantes taillées pour l'homme algérien moderne.",
            hero_image_url="https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=1920&q=80"
        )
        c2 = Collection.objects.create(
            name="Polos Old Money",
            slug="polos-old-money",
            description="Le polo revisité avec l'élégance intemporelle de la maison Old Money.",
            hero_image_url="https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=1920&q=80"
        )
        c3 = Collection.objects.create(
            name="Pantalons & Bas",
            slug="pantalons-bas",
            description="Des coupes minimalistes pour compléter votre style Old Money.",
            hero_image_url="https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=1920&q=80"
        )

        self.stdout.write('Creating 6 products...')

        p1 = Product.objects.create(
            name="Chemise Lin Classique",
            slug="chemise-lin-classique",
            description="Une chemise en lin naturel aux finitions soignées. Coupe droite, col classique, idéale pour les journées chaudes algériennes.",
            short_description="Chemise en lin premium, coupe droite élégante.",
            price=4500,
            discount_price=3990,
            status='PUBLISHED',
            is_featured=True,
            is_new_arrival=True
        )
        p1.collections.add(c1)
        ProductImage.objects.create(product=p1, image_url="https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800&q=80", is_main=True)
        ProductVariant.objects.create(product=p1, size='S', color='Blanc', stock=15)
        ProductVariant.objects.create(product=p1, size='S', color='Beige', stock=15)
        ProductVariant.objects.create(product=p1, size='M', color='Blanc', stock=20)
        ProductVariant.objects.create(product=p1, size='M', color='Beige', stock=20)
        ProductVariant.objects.create(product=p1, size='M', color='Bleu Ciel', stock=20)
        ProductVariant.objects.create(product=p1, size='L', color='Blanc', stock=15)
        ProductVariant.objects.create(product=p1, size='L', color='Beige', stock=15)
        ProductVariant.objects.create(product=p1, size='L', color='Bleu Ciel', stock=15)
        ProductVariant.objects.create(product=p1, size='XL', color='Blanc', stock=10)
        ProductVariant.objects.create(product=p1, size='XL', color='Beige', stock=10)

        p2 = Product.objects.create(
            name="Chemise Oxford Rayée",
            slug="chemise-oxford-rayee",
            description="La chemise Oxford rayée, indémodable du vestiaire Old Money. Tissu structuré, col boutonné, coupe ajustée.",
            short_description="Chemise Oxford rayée, coupe ajustée premium.",
            price=5200,
            status='PUBLISHED',
            is_bestseller=True
        )
        p2.collections.add(c1)
        ProductImage.objects.create(product=p2, image_url="https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800&q=80", is_main=True)
        ProductVariant.objects.create(product=p2, size='S', color='Bleu Marine', stock=10)
        ProductVariant.objects.create(product=p2, size='S', color='Blanc', stock=10)
        ProductVariant.objects.create(product=p2, size='M', color='Bleu Marine', stock=15)
        ProductVariant.objects.create(product=p2, size='M', color='Blanc', stock=15)
        ProductVariant.objects.create(product=p2, size='M', color='Vert', stock=15)
        ProductVariant.objects.create(product=p2, size='L', color='Bleu Marine', stock=10)
        ProductVariant.objects.create(product=p2, size='L', color='Blanc', stock=10)
        ProductVariant.objects.create(product=p2, size='XL', color='Bleu Marine', stock=8)

        p3 = Product.objects.create(
            name="Polo Piqué Signature",
            slug="polo-pique-signature",
            description="Notre polo signature en coton piqué de haute qualité. Le choix de l'homme algérien qui valorise l'élégance discrète.",
            short_description="Polo piqué coton premium, coupe slim fit.",
            price=3800,
            discount_price=3400,
            status='PUBLISHED',
            is_featured=True
        )
        p3.collections.add(c2)
        ProductImage.objects.create(product=p3, image_url="https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=800&q=80", is_main=True)
        for size in ['S', 'M', 'L', 'XL']:
            for color in ['Blanc', 'Noir', 'Vert Foncé']:
                if size == 'XL' and color == 'Vert Foncé':
                    continue
                stock = 20 if size in ['S', 'L'] else (25 if size == 'M' else 12)
                ProductVariant.objects.create(product=p3, size=size, color=color, stock=stock)
        ProductVariant.objects.create(product=p3, size='M', color='Beige', stock=25)

        p4 = Product.objects.create(
            name="Polo Mercerisé Luxe",
            slug="polo-mercerise-luxe",
            description="Un polo en coton mercerisé pour une brillance subtile et un toucher soyeux. L'élégance portée au quotidien.",
            short_description="Polo coton mercerisé, finition luxe.",
            price=4200,
            status='PUBLISHED',
            is_new_arrival=True
        )
        p4.collections.add(c2)
        ProductImage.objects.create(product=p4, image_url="https://images.unsplash.com/photo-1571455786673-9d9d6c194f90?w=800&q=80", is_main=True)
        ProductVariant.objects.create(product=p4, size='S', color='Blanc Cassé', stock=12)
        ProductVariant.objects.create(product=p4, size='S', color='Camel', stock=12)
        ProductVariant.objects.create(product=p4, size='M', color='Blanc Cassé', stock=18)
        ProductVariant.objects.create(product=p4, size='M', color='Camel', stock=18)
        ProductVariant.objects.create(product=p4, size='M', color='Noir', stock=18)
        ProductVariant.objects.create(product=p4, size='L', color='Blanc Cassé', stock=12)
        ProductVariant.objects.create(product=p4, size='L', color='Camel', stock=12)
        ProductVariant.objects.create(product=p4, size='XL', color='Camel', stock=8)
        ProductVariant.objects.create(product=p4, size='XL', color='Noir', stock=8)

        p5 = Product.objects.create(
            name="Pantalon Chino Premium",
            slug="pantalon-chino-premium",
            description="Le chino incontournable du style Old Money. Coupe droite légèrement slim, taille mi-haute, tissu stretch confortable.",
            short_description="Chino premium coupe slim, stretch confortable.",
            price=5800,
            discount_price=5200,
            status='PUBLISHED',
            is_featured=True,
            is_bestseller=True
        )
        p5.collections.add(c3)
        ProductImage.objects.create(product=p5, image_url="https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800&q=80", is_main=True)
        for size in ['S', 'M', 'L', 'XL']:
            for color in ['Beige', 'Kaki', 'Noir']:
                if size == 'XL' and color == 'Noir':
                    continue
                stock = 15 if size in ['S', 'L'] else (20 if size == 'M' else 10)
                ProductVariant.objects.create(product=p5, size=size, color=color, stock=stock)
        ProductVariant.objects.create(product=p5, size='M', color='Blanc', stock=20)

        p6 = Product.objects.create(
            name="Jean Slim Old Money",
            slug="jean-slim-old-money",
            description="Un jean slim en denim premium, délavé avec soin pour un look soigné et intemporel. La base de tout vestiaire Old Money.",
            short_description="Jean slim denim premium, délavage soigné.",
            price=6500,
            status='PUBLISHED',
            is_new_arrival=True
        )
        p6.collections.add(c3)
        ProductImage.objects.create(product=p6, image_url="https://images.unsplash.com/photo-1542272604-787c3835535d?w=800&q=80", is_main=True)
        for size in ['S', 'M', 'L', 'XL']:
            for color in ['Bleu Clair', 'Bleu Foncé', 'Noir']:
                if size in ['S', 'L'] and color == 'Noir':
                    continue
                if size == 'XL' and color == 'Bleu Clair':
                    continue
                stock = 12 if size in ['S', 'L'] else (18 if size == 'M' else 8)
                ProductVariant.objects.create(product=p6, size=size, color=color, stock=stock)

        self.stdout.write('Updating Homepage sections...')
        new_arrivals, _ = HomepageSection.objects.get_or_create(title="Nouveautés")
        new_arrivals.products.set([p1, p3, p6])
        new_arrivals.save()

        bestsellers, _ = HomepageSection.objects.get_or_create(title="Les Plus Vendus")
        bestsellers.products.set([p2, p5])
        bestsellers.save()

        recommendations, _ = HomepageSection.objects.get_or_create(title="Nos Recommandations")
        recommendations.products.set([p3, p4])
        recommendations.save()

        self.stdout.write('Updating Store Settings...')
        settings = StoreSettings.objects.first()
        if not settings:
            settings = StoreSettings.objects.create()
        settings.whatsapp_number = "0000000000"
        settings.save()

        self.stdout.write(self.style.SUCCESS('Demo data successfully seeded!'))

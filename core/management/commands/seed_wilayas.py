import json
from django.core.management.base import BaseCommand
from core.models import Wilaya

WILAYAS_DATA = [
    {"code": "01", "name": "Adrar"}, {"code": "02", "name": "Chlef"}, {"code": "03", "name": "Laghouat"},
    {"code": "04", "name": "Oum El Bouaghi"}, {"code": "05", "name": "Batna"}, {"code": "06", "name": "Bejaia"},
    {"code": "07", "name": "Biskra"}, {"code": "08", "name": "Bechar"}, {"code": "09", "name": "Blida"},
    {"code": "10", "name": "Bouira"}, {"code": "11", "name": "Tamanrasset"}, {"code": "12", "name": "Tebessa"},
    {"code": "13", "name": "Tlemcen"}, {"code": "14", "name": "Tiaret"}, {"code": "15", "name": "Tizi Ouzou"},
    {"code": "16", "name": "Algiers"}, {"code": "17", "name": "Djelfa"}, {"code": "18", "name": "Jijel"},
    {"code": "19", "name": "Setif"}, {"code": "20", "name": "Saida"}, {"code": "21", "name": "Skikda"},
    {"code": "22", "name": "Sidi Bel Abbes"}, {"code": "23", "name": "Annaba"}, {"code": "24", "name": "Guelma"},
    {"code": "25", "name": "Constantine"}, {"code": "26", "name": "Medea"}, {"code": "27", "name": "Mostaganem"},
    {"code": "28", "name": "M'Sila"}, {"code": "29", "name": "Mascara"}, {"code": "30", "name": "Ouargla"},
    {"code": "31", "name": "Oran"}, {"code": "32", "name": "El Bayadh"}, {"code": "33", "name": "Illizi"},
    {"code": "34", "name": "Bordj Bou Arreridj"}, {"code": "35", "name": "Boumerdes"}, {"code": "36", "name": "El Tarf"},
    {"code": "37", "name": "Tindouf"}, {"code": "38", "name": "Tissemsilt"}, {"code": "39", "name": "El Oued"},
    {"code": "40", "name": "Khenchela"}, {"code": "41", "name": "Souk Ahras"}, {"code": "42", "name": "Tipaza"},
    {"code": "43", "name": "Mila"}, {"code": "44", "name": "Ain Defla"}, {"code": "45", "name": "Naama"},
    {"code": "46", "name": "Ain Temouchent"}, {"code": "47", "name": "Ghardaia"}, {"code": "48", "name": "Relizane"},
    {"code": "49", "name": "El M'Ghair"}, {"code": "50", "name": "El Menia"}, {"code": "51", "name": "Ouled Djellal"},
    {"code": "52", "name": "Bordj Baji Mokhtar"}, {"code": "53", "name": "Beni Abbes"}, {"code": "54", "name": "Timimoun"},
    {"code": "55", "name": "Touggourt"}, {"code": "56", "name": "Djanet"}, {"code": "57", "name": "In Salah"},
    {"code": "58", "name": "In Guezzam"}
]

class Command(BaseCommand):
    help = 'Seeds the database with the 58 Wilayas of Algeria'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Wilayas...')
        created_count = 0
        for w_data in WILAYAS_DATA:
            wilaya, created = Wilaya.objects.get_or_create(
                code=w_data['code'],
                defaults={
                    'name': w_data['name'],
                    'home_delivery_price': 800.00,
                    'bureau_delivery_price': 500.00,
                    'delivery_days': '2-4 days',
                    'is_active': True
                }
            )
            # If it already existed but name was spelled differently, we optionally update it here,
            # but getting it or creating is sufficient as per the prompt's request.
            if created:
                created_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} new Wilayas.'))

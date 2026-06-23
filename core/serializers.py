from rest_framework import serializers
from .models import Wilaya, StoreSettings, HomepageContent, HomepageSection
from products.models import Product
from products.serializers import ProductSerializer

class WilayaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wilaya
        fields = '__all__'

class StoreSettingsSerializer(serializers.ModelSerializer):
    theme_colors = serializers.SerializerMethodField()

    class Meta:
        model = StoreSettings
        fields = '__all__'

    def get_theme_colors(self, obj):
        themes = {
            'dark-classique': {'bg': '#0A0A0A', 'text': '#F5F0E8', 'accent': '#D4AF37', 'cards': '#1A1A1A', 'primary': '#1B5E20'},
            'green-luxury': {'bg': '#0D2B0D', 'text': '#F5F0E8', 'accent': '#D4AF37', 'cards': '#1A3D1A', 'primary': '#1B5E20'},
            'forest-gold': {'bg': '#1B3A1B', 'text': '#FFFFFF', 'accent': '#D4AF37', 'cards': '#243D24', 'primary': '#2E7D32'},
            'black-green': {'bg': '#0A0A0A', 'text': '#FFFFFF', 'accent': '#2E7D32', 'cards': '#111111', 'primary': '#2E7D32'},
            'gold-dark': {'bg': '#1A1400', 'text': '#F5F0E8', 'accent': '#D4AF37', 'cards': '#2A2000', 'primary': '#8D6E00'},
            'pure-green': {'bg': '#1B5E20', 'text': '#FFFFFF', 'accent': '#D4AF37', 'cards': '#2E7D32', 'primary': '#1B5E20'},
        }
        
        if obj.active_theme == 'custom':
            return {
                'bg': obj.custom_bg_color or '#0A0A0A',
                'text': obj.custom_text_color or '#F5F0E8',
                'accent': obj.custom_accent_color or '#D4AF37',
                'cards': obj.custom_cards_color or '#1A1A1A',
                'primary': obj.custom_primary_color or '#1B5E20',
            }
            
        return themes.get(obj.active_theme, themes['dark-classique'])

class HomepageContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomepageContent
        fields = '__all__'

class HomepageSectionSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Product.objects.all(),
        required=False
    )

    class Meta:
        model = HomepageSection
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['products'] = ProductSerializer(instance.products.all(), many=True).data
        return rep



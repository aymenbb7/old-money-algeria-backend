from rest_framework import serializers
from .models import Wilaya, StoreSettings, HomepageContent, LookbookItem

class WilayaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wilaya
        fields = '__all__'

class StoreSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreSettings
        fields = '__all__'

class HomepageContentSerializer(serializers.ModelSerializer):
    hero_image = serializers.SerializerMethodField()
    collections_hero_image = serializers.SerializerMethodField()

    class Meta:
        model = HomepageContent
        fields = '__all__'

    def get_hero_image(self, obj):
        if obj.hero_image:
            return obj.hero_image.url
        return None

    def get_collections_hero_image(self, obj):
        if obj.collections_hero_image:
            return obj.collections_hero_image.url
        return None

class LookbookItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = LookbookItem
        fields = '__all__'

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

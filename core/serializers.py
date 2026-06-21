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
    class Meta:
        model = HomepageContent
        fields = '__all__'

class LookbookItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LookbookItem
        fields = '__all__'

from rest_framework import serializers
from .models import Brand, Product, LicenseKey, License, Activation

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'brand', 'name', 'slug', 'created_at']

class ActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activation
        fields = ['id', 'instance_id', 'activated_at']

class LicenseSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    brand_name = serializers.ReadOnlyField(source='product.brand.name')
    activations = ActivationSerializer(many=True, read_only=True)
    active_seats = serializers.IntegerField(source='activations.count', read_only=True)

    class Meta:
        model = License
        fields = [
            'id', 'product', 'product_name', 'brand_name', 'status', 
            'expires_at', 'total_seats', 'active_seats', 'activations', 'created_at'
        ]

class LicenseKeySerializer(serializers.ModelSerializer):
    licenses = LicenseSerializer(many=True, read_only=True)
    brand_name = serializers.ReadOnlyField(source='brand.name')

    class Meta:
        model = LicenseKey
        fields = ['id', 'key', 'customer_email', 'brand', 'brand_name', 'licenses', 'created_at']

# Specialized Serializers for User Stories

class ProvisionLicenseSerializer(serializers.Serializer):
    brand_slug = serializers.SlugField()
    product_slug = serializers.SlugField()
    customer_email = serializers.EmailField()
    license_key = serializers.CharField(required=False, allow_blank=True)
    total_seats = serializers.IntegerField(default=1)
    expiration_days = serializers.IntegerField(required=False, default=365)

class ActivateLicenseSerializer(serializers.Serializer):
    license_key = serializers.CharField()
    instance_id = serializers.CharField()
    product_slug = serializers.SlugField()

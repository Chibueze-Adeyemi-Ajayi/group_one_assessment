from rest_framework import status, views, permissions, generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Brand, Product, LicenseKey, License, Activation
from .serializers import (
    LicenseKeySerializer, LicenseSerializer, 
    ProvisionLicenseSerializer, ActivateLicenseSerializer
)
from drf_spectacular.utils import extend_schema

class ProvisionLicenseView(views.APIView):
    """
    US1: Brand can provision a license.
    Allows a brand to create a license key or add a product to an existing key.
    """
    permission_classes = [permissions.IsAuthenticated] # In real life, check for Brand-specific permissions

    @extend_schema(request=ProvisionLicenseSerializer, responses={201: LicenseKeySerializer})
    def post(self, request):
        serializer = ProvisionLicenseSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            brand = get_object_or_404(Brand, slug=data['brand_slug'])
            product = get_object_or_404(Product, brand=brand, slug=data['product_slug'])
            
            # Find or create LicenseKey
            if data.get('license_key'):
                lk = get_object_or_404(LicenseKey, key=data['license_key'], brand=brand)
            else:
                lk = LicenseKey.objects.create(
                    customer_email=data['customer_email'],
                    brand=brand
                )
            
            # Create the License
            expires_at = timezone.now() + timedelta(days=data['expiration_days'])
            License.objects.create(
                license_key=lk,
                product=product,
                expires_at=expires_at,
                total_seats=data['total_seats']
            )
            
            return Response(LicenseKeySerializer(lk).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_USER_INPUT)

class ActivateLicenseView(views.APIView):
    """
    US3: End-user product can activate a license.
    """
    permission_classes = [permissions.AllowAny] # Products usually use a License Key, not a User Token

    @extend_schema(request=ActivateLicenseSerializer, responses={200: LicenseSerializer})
    def post(self, request):
        serializer = ActivateLicenseSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            lk = get_object_or_404(LicenseKey, key=data['license_key'])
            license_obj = get_object_or_404(License, license_key=lk, product__slug=data['product_slug'])
            
            if not license_obj.is_active():
                return Response({"error": "License is not active or expired."}, status=status.HTTP_403_FORBIDDEN)
            
            # Check seat limit
            if license_obj.activations.count() >= license_obj.total_seats:
                # Check if this instance is already activated (idempotency)
                if not Activation.objects.filter(license=license_obj, instance_id=data['instance_id']).exists():
                    return Response({"error": "No seats remaining."}, status=status.HTTP_409_CONFLICT)
            
            # Register activation
            Activation.objects.get_or_create(
                license=license_obj,
                instance_id=data['instance_id']
            )
            
            return Response(LicenseSerializer(license_obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_USER_INPUT)

class LicenseStatusView(views.APIView):
    """
    US4: User can check license status.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses={200: LicenseKeySerializer})
    def get(self, request, key):
        lk = get_object_or_404(LicenseKey, key=key)
        return Response(LicenseKeySerializer(lk).data)

class CustomerLicenseListView(generics.ListAPIView):
    """
    US6: Brands can list licenses by customer email across all brands.
    """
    serializer_class = LicenseKeySerializer
    permission_classes = [permissions.IsAuthenticated] # Admin only

    def get_queryset(self):
        email = self.request.query_params.get('email')
        if email:
            return LicenseKey.objects.filter(customer_email=email)
        return LicenseKey.objects.none()

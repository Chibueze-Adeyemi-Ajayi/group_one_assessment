from rest_framework import status, views, permissions, generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Brand, Product, LicenseKey, License, Activation
from .serializers import (
    BrandSerializer, ProductSerializer,
    LicenseKeySerializer, LicenseSerializer, 
    ProvisionLicenseSerializer, ActivateLicenseSerializer
)
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

@extend_schema_view(
    post=extend_schema(tags=['Auth'])
)
class DecoratedTokenObtainPairView(TokenObtainPairView):
    pass

@extend_schema_view(
    post=extend_schema(tags=['Auth'])
)
class DecoratedTokenRefreshView(TokenRefreshView):
    pass

class ProvisionLicenseView(views.APIView):
    """
    US1: Brand can provision a license.
    Allows a brand to create a license key or add a product to an existing key.
    """
    permission_classes = [permissions.IsAuthenticated] 

    @extend_schema(request=ProvisionLicenseSerializer, responses={201: LicenseKeySerializer}, tags=['License'])
    def post(self, request):
        serializer = ProvisionLicenseSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            brand = get_object_or_404(Brand, slug=data['brand_slug'])
            product = get_object_or_404(Product, brand=brand, slug=data['product_slug'])
            
            license_key_str = data.get('license_key')
            
            if license_key_str:
                # 1. Check if this key exists anywhere in the system
                existing_key = LicenseKey.objects.filter(key=license_key_str).first()
                
                if existing_key:
                    # If it exists, it MUST belong to the same brand
                    if existing_key.brand != brand:
                        return Response(
                            {"error": f"License key '{license_key_str}' is already assigned to another brand."},
                            status=status.HTTP_409_CONFLICT
                        )
                    lk = existing_key
                else:
                    # If it doesn't exist at all, create it for this brand
                    lk = LicenseKey.objects.create(
                        key=license_key_str,
                        customer_email=data['customer_email'],
                        brand=brand
                    )
            else:
                # 2. US1 Logic: If no key provided, check if user already has a key for THIS brand
                lk = LicenseKey.objects.filter(
                    customer_email=data['customer_email'], 
                    brand=brand
                ).first()
                
                # 3. Create new auto-generated key if user doesn't have one for this brand yet
                if not lk:
                    lk = LicenseKey.objects.create(
                        customer_email=data['customer_email'],
                        brand=brand
                    )
            
            # Create the License (Entitlement)
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
    permission_classes = [permissions.AllowAny] 

    @extend_schema(request=ActivateLicenseSerializer, responses={200: LicenseSerializer}, tags=['License'])
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

    @extend_schema(responses={200: LicenseKeySerializer}, tags=['License'])
    def get(self, request, key):
        lk = get_object_or_404(LicenseKey, key=key)
        return Response(LicenseKeySerializer(lk).data)

@extend_schema(
    tags=['License'],
    parameters=[
        OpenApiParameter("email", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Customer email to look up")
    ]
)
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

@extend_schema(tags=['Brand'])
class BrandListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list or create Brands.
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticated]

@extend_schema(tags=['Brand'])
class ProductListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list or create Products for a brand.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

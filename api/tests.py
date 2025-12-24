from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from api.models import Brand, Product, LicenseKey, License, Activation
from django.utils import timezone
from datetime import timedelta

class LicenseAPITestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_superuser(username='admin', password='password123', email='admin@test.com')
        self.client = APIClient()
        
        # Get JWT token
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'admin',
            'password': 'password123'
        })
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create Initial Data
        self.brand = Brand.objects.create(name="Brand One", slug="brand-one")
        self.product = Product.objects.create(brand=self.brand, name="Product A", slug="prod-a")

    def test_brand_isolation(self):
        # Create another brand
        other_brand = Brand.objects.create(name="Brand Two", slug="brand-two")
        
        # Try to provision for Brand One using a key from Brand Two
        key_two = LicenseKey.objects.create(key="key-two", brand=other_brand, customer_email="test@test.com")
        
        response = self.client.post(reverse('provision-license'), {
            "brand_slug": "brand-one",
            "product_slug": "prod-a",
            "customer_email": "test@test.com",
            "license_key": "key-two"
        })
        
        # Should be a Conflict because the key belongs to another brand
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_license_provisioning_and_activation(self):
        # 1. Provision
        response = self.client.post(reverse('provision-license'), {
            "brand_slug": "brand-one",
            "product_slug": "prod-a",
            "customer_email": "customer@test.com",
            "total_seats": 2,
            "expiration_days": 30
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        license_key = response.data['key']
        
        # 2. Activate Site 1 (Success)
        self.client.credentials() # Clear auth to simulate end-user product
        response = self.client.post(reverse('activate-license'), {
            "license_key": license_key,
            "product_slug": "prod-a",
            "instance_id": "site1.com"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Activate Site 2 (Success)
        response = self.client.post(reverse('activate-license'), {
            "license_key": license_key,
            "product_slug": "prod-a",
            "instance_id": "site2.com"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Activate Site 3 (Fail - Seat Limit)
        response = self.client.post(reverse('activate-license'), {
            "license_key": license_key,
            "product_slug": "prod-a",
            "instance_id": "site3.com"
        })
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("No seats remaining", response.data['error'])

    def test_idempotency_activation(self):
        # Provision a key
        response = self.client.post(reverse('provision-license'), {
            "brand_slug": "brand-one",
            "product_slug": "prod-a",
            "customer_email": "customer@test.com",
            "total_seats": 1
        })
        license_key = response.data['key']
        
        self.client.credentials()
        
        # First activation
        response = self.client.post(reverse('activate-license'), {
            "license_key": license_key,
            "product_slug": "prod-a",
            "instance_id": "site1.com"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Second activation from same site (Should succeed even if seat is 1)
        response = self.client.post(reverse('activate-license'), {
            "license_key": license_key,
            "product_slug": "prod-a",
            "instance_id": "site1.com"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_lookup(self):
        # Create multiple keys for same customer
        LicenseKey.objects.create(key="key1", brand=self.brand, customer_email="lookup@test.com")
        other_brand = Brand.objects.create(name="Other", slug="other")
        LicenseKey.objects.create(key="key2", brand=other_brand, customer_email="lookup@test.com")
        
        # Use auth
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(reverse('customer-license-list'), {'email': 'lookup@test.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

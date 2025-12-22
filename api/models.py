from django.db import models
from django.utils import timezone
import uuid

class Brand(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('brand', 'slug')

    def __str__(self):
        return f"{self.brand.name} - {self.name}"

class LicenseKey(models.Model):
    key = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    customer_email = models.EmailField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='license_keys')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.key} ({self.customer_email})"

class License(models.Model):
    STATUS_CHOICES = (
        ('VALID', 'Valid'),
        ('SUSPENDED', 'Suspended'),
        ('CANCELLED', 'Cancelled'),
    )

    license_key = models.ForeignKey(LicenseKey, on_delete=models.CASCADE, related_name='licenses')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='licenses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='VALID')
    expires_at = models.DateTimeField(null=True, blank=True)
    total_seats = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_active(self):
        if self.status != 'VALID':
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def __str__(self):
        return f"{self.product.name} license for {self.license_key.key}"

class Activation(models.Model):
    license = models.ForeignKey(License, on_delete=models.CASCADE, related_name='activations')
    instance_id = models.CharField(max_length=255) # e.g. Site URL or Machine ID
    activated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('license', 'instance_id')

    def __str__(self):
        return f"{self.instance_id} on {self.license.product.name}"

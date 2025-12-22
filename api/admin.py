from django.contrib import admin
from .models import Brand, Product, LicenseKey, License, Activation

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'slug')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'slug', 'created_at')
    list_filter = ('brand',)
    search_fields = ('name', 'slug')

@admin.register(LicenseKey)
class LicenseKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'customer_email', 'brand', 'created_at')
    list_filter = ('brand',)
    search_fields = ('key', 'customer_email')

class LicenseActivationInline(admin.TabularInline):
    model = Activation
    extra = 0
    readonly_fields = ('instance_id', 'activated_at')

@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('product', 'license_key', 'status', 'expires_at', 'total_seats', 'active_seats')
    list_filter = ('status', 'product__brand', 'product')
    search_fields = ('license_key__key', 'license_key__customer_email')
    inlines = [LicenseActivationInline]

    def active_seats(self, obj):
        return obj.activations.count()

@admin.register(Activation)
class ActivationAdmin(admin.ModelAdmin):
    list_display = ('instance_id', 'license', 'activated_at')
    search_fields = ('instance_id', 'license__license_key__key')

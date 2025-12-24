from django.urls import path
from .views import (
    BrandListCreateView, ProductListCreateView,
    ProvisionLicenseView, ActivateLicenseView, 
    LicenseStatusView, CustomerLicenseListView
)

urlpatterns = [
    path('brands/', BrandListCreateView.as_view(), name='brand-list'),
    path('products/', ProductListCreateView.as_view(), name='product-list'),
    path('provision/', ProvisionLicenseView.as_view(), name='provision-license'),
    path('activate/', ActivateLicenseView.as_view(), name='activate-license'),
    path('status/<str:key>/', LicenseStatusView.as_view(), name='license-status'),
    path('customer-lookup/', CustomerLicenseListView.as_view(), name='customer-license-list'),
]

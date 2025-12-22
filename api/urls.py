from django.urls import path
from .views import (
    ProvisionLicenseView, ActivateLicenseView, 
    LicenseStatusView, CustomerLicenseListView
)

urlpatterns = [
    path('provision/', ProvisionLicenseView.as_view(), name='provision-license'),
    path('activate/', ActivateLicenseView.as_view(), name='activate-license'),
    path('status/<str:key>/', LicenseStatusView.as_view(), name='license-status'),
    path('customer-lookup/', CustomerLicenseListView.as_view(), name='customer-license-list'),
]

from django.urls import path , include
from . import views

urlpatterns = [
    path('AdminLogin/',views.AdminLoginAPI),
    path('Invoices/',views.InvoicesAPI),
    # interest credited to current user of fractional unit of invoice
]
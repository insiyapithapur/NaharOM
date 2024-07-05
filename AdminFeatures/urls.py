from django.urls import path , include
from . import views

urlpatterns = [
    path('AdminLogin/',views.AdminLoginAPI),
    path('Invoices/',views.InvoicesAPI),
    path('SalesPurchasedReport/<int:User_id>',views.SalesPurchasedReportAPI),
]
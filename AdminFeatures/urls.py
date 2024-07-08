from django.urls import path , include
from . import views

urlpatterns = [
    path('AdminLogin/',views.AdminLoginAPI),
    path('ExtractInvoicesAPI/',views.ExtractInvoicesAPI),
    path('GetInvoices/<int:user_id>/', views.GetInvoicesAPI), # primary to secondary all invoices show
    path('GetInvoices/<int:user_id>/<int:primary_invoice_id>/', views.GetInvoicesAPI), #particular 1 invoice fetch 
    path('PostInvoice/',views.PostInvoiceAPI),
    path('SalesPurchasedReport/<int:User_id>',views.SalesPurchasedReportAPI),
]
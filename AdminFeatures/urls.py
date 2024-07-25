from django.urls import path , include
from . import views

urlpatterns = [
    path('Login/',views.LoginAPI),
    path('ExtractInvoicesAPI/',views.ExtractInvoicesAPI),
    # used to send all invoices from primary to secondary platform
    path('GetInvoices/<int:user_id>/', views.GetInvoicesAPI), # primary to secondary all invoices show
    path('GetInvoices/<int:user_id>/<int:primary_invoice_id>/', views.GetInvoicesAPI), #particular 1 invoice fetch 
    path('InvoiceMgt/<int:user_id>/',views.InvoiceAPI),
    # used to store invoice that admin will post
    path('PostInvoice/',views.PostInvoiceAPI),
    path('SalesPurchasedReport/<int:User_id>/',views.SalesPurchasedReportAPI),
    path('UserManagement/',views.UserManagementAPI),
    path('GenerateToken/<int:admin_id>/<int:user_role_id>/',views.GenerateTokenAPI),
    path('userPersonate/<int:token>/',views.UserPersonateAPI),
]
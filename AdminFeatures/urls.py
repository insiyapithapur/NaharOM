from django.urls import path , include
from . import views

urlpatterns = [
    path('ExtractInvoicesAPI/',views.ExtractInvoicesAPI),
    # used to send all invoices from primary to secondary platform
    path('GetInvoices/<int:user_id>/', views.GetInvoicesAPI),
    #particular 1 invoice fetch from primary
    path('GetInvoices/<int:user_id>/<int:primary_invoice_id>/', views.GetInvoicesAPI),
    # used to send all invoice ( admin posted + admin not posted means primary one )
    path('InvoiceMgt/<int:user>',views.InvoiceMgtAPI),  #DONE
    # used to post invoice that admin want to
    path('PostInvoice/',views.PostInvoiceAPI), #DONE
    path('SalesPurchasedReport/<int:User_id>/',views.SalesPurchasedReportAPI),
    path('UserManagement/<int:user>',views.UserManagementAPI), #DONE
    # path('usersLedger/<int:user>',views.usersLedgerAPI),
    path('GenerateToken/<int:admin_id>/<int:user_role_id>/',views.GenerateTokenAPI),
    path('userPersonate/<slug:token>/',views.UserPersonateAPI),
]
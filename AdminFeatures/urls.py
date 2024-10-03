from django.urls import path , include
from . import views

urlpatterns = [
    path('ExtractInvoicesAPI/',views.ExtractInvoicesAPI),
    # used to send all invoices from primary to secondary platform
    path('GetInvoices/<int:user_id>/', views.GetInvoicesAPI),
    #particular 1 invoice fetch from primary
    path('GetInvoices/<int:user_id>/<int:primary_invoice_id>/', views.GetInvoicesAPI),

    # used to send all invoice (  fractionalized_invoice_data , unfractionalized_invoice_data  ,Partial_unfractionalized_invoice_data )
    path('InvoiceMgt/<int:user>',views.InvoiceMgtAPI),  #DONE
    path('configurations/',views.ConfigurationAPI), #DONE
    # used to post invoice that admin want to
    path('PostInvoice/',views.PostInvoiceAPI), #DONE
    path('OnboardingReport/<int:user>',views.UserManagementAPI), #DONE
    path('transactionReport/<int:user>',views.usersLedgerAPI),
    path('SalesPurchasedReport/<int:user>',views.SalesPurchasedReportAPI),
    path('TdsReport/<int:user>',views.TdsReportAPI),
    path('BidReport/<int:user>',views.BidReportAPI),
    path('TradingActivityReport/<int:user>',views.TradingActivityReportAPI),
    path('APIMgtReport/<int:user>',views.APIMgtReportAPI),

    
    path('GenerateToken/<int:admin_id>/<int:user_role_id>/',views.GenerateTokenAPI),
    path('userPersonate/<slug:token>/',views.UserPersonateAPI),
]
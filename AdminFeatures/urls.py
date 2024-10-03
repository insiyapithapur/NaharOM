from django.urls import path , include
from . import views
from .views import UserPersonateAPI
from .views import TransactionLogAPI

urlpatterns = [
    path('ExtractInvoicesAPI/',views.ExtractInvoicesAPI, name='extract_invoices_api'),
    path('transaction-logs/', TransactionLogAPI.as_view(), name='transaction_log_api'),
    path('GetInvoices/<int:user_id>/', views.GetInvoicesAPI),
    path('GetInvoices/<int:user_id>/<int:primary_invoice_id>/', views.GetInvoicesAPI),
    path('InvoiceMgt/<int:user>',views.InvoiceMgtAPI),  #DONE
    path('configurations/',views.ConfigurationAPI), #DONE
    path('PostInvoice/',views.PostInvoiceAPI), #DONE
    path('OnboardingReport/<int:user>',views.UserManagementAPI), #DONE
    path('transactionReport/<int:user>',views.usersLedgerAPI),
    path('SalesPurchasedReport/<int:user>',views.SalesPurchasedReportAPI),
    path('TdsReport/<int:user>',views.TdsReportAPI),
    path('BidReport/<int:user>',views.BidReportAPI),
    path('TradingActivityReport/<int:user>',views.TradingActivityReportAPI),
    path('APIMgtReport/<int:user>',views.APIMgtReportAPI),
    path('GenerateToken/<int:admin_id>/<int:user_role_id>/',views.GenerateTokenAPI),
    path('impersonate/<int:admin_id>/<int:user_role_id>/', UserPersonateAPI.as_view(), name='user_impersonate_api'),
]

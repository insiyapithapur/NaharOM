from django.urls import path , include
from . import views

urlpatterns = [
    path('Login/',views.LoginAPI),
    path('Register/',views.RegisterAPI),
    path('LoginAsIndividual/',views.LoginAsIndividualAPI),
    path('LoginAsCompany/',views.LoginAsCompanyAPI),
    path('BankAccDetails/',views.BankAccDetailsAPI),
    path('PanCardNo/',views.PanCardDetailsAPI),
    # path('generateotp/<int:user_role_id>',views.GenerateOTPAPI),
    path('AddFunds/',views.AddFundsAPI),
    path('CheckBooleans/<int:user_role_id>',views.CheckBooleansAPI),
    path('AdminLogin/',views.AdminLoginAPI),
    path('Invoices/',views.InvoicesAPI),
    path('ToBuy/<int:invoice_secondary_id>/<int:user_role_id>/<int:wallet_id>',views.TobuyAPI),
    path('BuyerIRR/<int:user_role_id>',views.BuyerIRRAPI),
    

    path('SecurityQuestion/',views.SecurityQuestionAPI),
]
from django.urls import path , include
from . import views

urlpatterns = [
    path('Login/',views.LoginAPI),
    path('Register/',views.RegisterAPI),
    path('BankAccDetails/',views.BankAccDetailsAPI), 
    path('Credit_Funds/',views.Credit_FundsAPI), #bank_to_wallet
    path('ledger/<int:user_role_id>',views.LedgerAPI),
    path('ToBuy/',views.TobuyAPI), #wallet_to_buy
    path('PostForSell/',views.ToSellAPI), #sell_to_wallet
    # path('BuyerIRR/<int:invoice_id>',views.BuyerIRRAPI),
    path('GetDetails/<int:user_role_id>',views.GetDetails),
    path('AdminSettings/', views.create_entry, name='create_entry'),
    path('showFunds/<int:user_role_id>',views.ShowFundsAPI),
    path('generateOTP/',views.GenerateOtpAPI),
    path('verifyOtp/',views.VerifyOtpAPI),
]
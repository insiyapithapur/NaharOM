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
    path('BuyerIRR/<int:user_role_id>',views.BuyerIRRAPI),
    path('GetInvoice/',views.GetInvoice),
]
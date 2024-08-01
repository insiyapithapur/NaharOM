from django.urls import path , include
from . import views

#  user = user role id
urlpatterns = [
    # path('Login/',views.LoginAPI),
    # path('Register/',views.RegisterAPI),
    path('generateOTP/',views.GenerateOtpAPI),
    path('verifyOtp/',views.VerifyOtpAPI), #DONE
    path('verifyStatus/<int:user>',views.verifyStatusAPI), #DONE
    path('phoneToPrefill/<int:user>',views.phonetoPrefillAPI), #DONE
    path('Profile/',views.ProfileAPI), #DONE
    path('Profile/<int:user>',views.ProfileAPI),
    # path('GetUserDetails/<int:user_id>/',views.GetUserDetailsAPI), #details fetach karavis ane user_role store karis
    # path('status/',views.ChanageStatusAPI),
    path('BankAccDetails/',views.BankAccDetailsAPI), #DONE
    path('Credit_Funds/',views.Credit_FundsAPI), #bank_to_wallet
    path('ledger/<int:user>',views.LedgerAPI), #DONE
    path('GetSellPurchaseDetails/<int:user>',views.GetSellPurchaseDetailsAPI),
    path('ToBuy/',views.TobuyAPI), #wallet_to_buy
    path('PostForSell/',views.ToSellAPI), #sell_to_wallet
    # path('BuyerIRR/<int:invoice_id>',views.BuyerIRRAPI),
    path('AdminSettings/', views.create_entry, name='create_entry'),
    path('showFunds/<int:user_role_id>',views.ShowFundsAPI),
    path('cashFlow/<int:invoiceID>/',views.cashFlowAPI)
]
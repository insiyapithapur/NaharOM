from django.urls import path , include
from . import views

#  user = user role id
urlpatterns = [
    path('generateOTP/',views.GenerateOtpAPI),
    path('verifyOtp/',views.VerifyOtpAPI), #DONE
    path('verifyStatus/<int:user>',views.verifyStatusAPI), #DONE
    path('phoneToPrefill/<int:user>',views.phonetoPrefillAPI), #DONE
    path('Profile/',views.ProfileAPI), #DONE
    path('Profile/<int:user>',views.ProfileAPI), #DONE
    path('BankAccDetails/',views.BankAccDetailsAPI), #DONE
    path('Credit_Funds/',views.Credit_FundsAPI), #bank_to_wallet #DONE
    path('ledger/<int:user>',views.LedgerAPI), #DONE
    path('showFunds/<int:user_role_id>',views.ShowFundsAPI),
    path('GetSellPurchaseDetails/<int:user>',views.GetSellPurchaseDetailsAPI), #DONE
    path('ToBuy/',views.TobuyAPI), #wallet_to_buy #DONE
    path('PostForSell/',views.ToSellAPI), #sell_to_wallet #DONE
    path('cashFlow/<int:invoiceID>/',views.cashFlowAPI)
]
from django.urls import path , include
from . import views

#  user = user role id
urlpatterns = [
    path('generateOTP/',views.GenerateOtpAPI),
    path('verifyOtp/',views.VerifyOtpAPI), #DONE
    path('verifyStatus/<int:user>',views.verifyStatusAPI), #DONE
    path('phoneToPrefill/<int:user>',views.phonetoPrefillAPI),   #change name
    path('PAN_TO_GST/',views.PAN_TO_GSTAPI),
    path('Profile/',views.ProfileAPI), #DONE
    path('Profile/<int:user>',views.ProfileAPI), #DONE
    path('BankAccDetails/',views.BankAccDetailsAPI), #DONE
    path('Credit_Funds/',views.Credit_FundsAPI), #bank_to_wallet #DONE
    path('Withdraw_Funds/',views.Withdraw_FundsAPI),
    path('ledger/<int:user>',views.LedgerAPI), #DONE
    path('showFunds/<int:user_role_id>',views.ShowFundsAPI),
    path('GetSellPurchaseDetails/<int:user>',views.GetSellPurchaseDetailsAPI), #DONE
    path('ToBuy/',views.TobuyAPI), #wallet_to_buy #DONE
    path('PostForSell/',views.ToSellAPI), #sell_to_wallet #DONE
    path('checkBalanceAgainstBidPrice/',views.checkBalanceAgainstBidPrice),
    path('proceedToBid/',views.proceedToBid),
    path('modifyBid/',views.ModifyBidAPI),
    path('withdrawBid/',views.withdrawBid),
    path('acceptBid/',views.AcceptBidAPI),
    path('cashFlow/<int:invoiceID>/',views.cashFlowAPI)
]
from django.urls import path , include
from . import views

#  user = user role id
urlpatterns = [
    path('generate-otp/',views.GenerateOtpAPI),
    path('verify-otp/',views.VerifyOtpAPI), #DONE
    path('verify-status/<int:user>',views.verifyStatusAPI), #DONE
    path('phone-to-prefill/<int:user>',views.phonetoPrefillAPI),   #change name
    path('pan-to-gst/',views.PAN_TO_GSTAPI),
    path('profile/',views.ProfileAPI), #DONE
    path('profile/<int:user>',views.ProfileAPI), #DONE
    path('bank-account-details/',views.BankAccDetailsAPI), #DONE
    path('credit-funds/',views.Credit_FundsAPI), #bank_to_wallet #DONE
    path('withdraw-funds/',views.Withdraw_FundsAPI),
    path('ledger/<int:user>',views.LedgerAPI), #DONE
    path('show-funds/<int:user_role_id>',views.ShowFundsAPI),
    path('get-sell-purchase-details/<int:user>',views.GetSellPurchaseDetailsAPI), #DONE
    path('to-buy/',views.TobuyAPI), #wallet_to_buy #DONE
    path('post-for-sell/',views.ToSellAPI), #sell_to_wallet #DONE
    path('check-balance-against-bid-price/',views.checkBalanceAgainstBidPrice),
    path('proceed-to-bid/',views.proceedToBid),
    path('modify-bid/',views.ModifyBidAPI),
    path('withdraw-bid/',views.withdrawBid),
    path('accept-bid/',views.AcceptBidAPI),
    path('cash-flow/<int:invoiceID>/',views.cashFlowAPI)
]

from django.urls import path , include
from . import views

#  user = user role id
urlpatterns = [
    # path('Login/',views.LoginAPI),
    # path('Register/',views.RegisterAPI),
    path('generateOTP/',views.GenerateOtpAPI),
    path('verifyOtp/',views.VerifyOtpAPI),
    path('verifyStatus/<int:user>',views.verifyStatusAPI),
    path('phoneToPrefill/<int:user>/',views.phonetoPrefillAPI),
    path('submitProfile/',views.SubmitProfileAPI),
    path('Profile/<int:user>',views.SubmitProfileAPI),
    # path('GetUserDetails/<int:user_id>/',views.GetUserDetailsAPI), #details fetach karavis ane user_role store karis
    # path('status/',views.ChanageStatusAPI),
    # pancard enter api
    # phone to prefill 
    # company pancard --> dettails fetch
    # manually entered
    path('BankAccDetails/',views.BankAccDetailsAPI), 
    path('Credit_Funds/',views.Credit_FundsAPI), #bank_to_wallet
    path('ledger/<int:user>',views.LedgerAPI),
    path('GetDetails/<int:user>',views.GetDetails),
    path('ToBuy/',views.TobuyAPI), #wallet_to_buy
    path('PostForSell/',views.ToSellAPI), #sell_to_wallet
    # path('BuyerIRR/<int:invoice_id>',views.BuyerIRRAPI),
    path('AdminSettings/', views.create_entry, name='create_entry'),
    path('showFunds/<int:user_role_id>',views.ShowFundsAPI),
    path('cashFlow/<int:invoiceID>/',views.cashFlowAPI)
]
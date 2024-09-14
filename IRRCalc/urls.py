from django.urls import path
from . import views

urlpatterns = [
    path('fixed_price/',views.FixedPriceIRRAPI),
    path('declining_principal/',views.DecliningPrincipalAPI),
    path('balloon_payment/',views.BalloonPaymentAPI)
]
from django.urls import path
from . import views

urlpatterns = [
    path('fixed_price/',views.FixedPriceIRRAPI),
]
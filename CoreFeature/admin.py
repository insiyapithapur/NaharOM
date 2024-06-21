from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.BankAccountDetails)
admin.site.register(models.CompanyDetails)
admin.site.register(models.IndividualDetails)
admin.site.register(models.PanCardNos)
admin.site.register(models.SecurityQuestion)
admin.site.register(models.UserRole)
admin.site.register(models.Wallet)
admin.site.register(models.WalletTransaction)
admin.site.register(models.Buyer)
admin.site.register(models.Invoices)
admin.site.register(models.Seller)
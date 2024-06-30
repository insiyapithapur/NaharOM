from django.contrib import admin
from . import models

admin.site.register(models.User)
admin.site.register(models.UserRole)
admin.site.register(models.IndividualDetails)
admin.site.register(models.CompanyDetails)
admin.site.register(models.PanCardNos)
admin.site.register(models.BankAccountDetails)
admin.site.register(models.Invoices)
admin.site.register(models.Buyers)
admin.site.register(models.FractionalUnits)
admin.site.register(models.OutstandingBalance)
admin.site.register(models.Sellers)
admin.site.register(models.SalePurchaseReport)
admin.site.register(models.OutstandingBalanceTransaction)
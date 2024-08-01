from datetime import time
from django.utils import timezone
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager , PermissionsMixin
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, mobile, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not mobile:
            raise ValueError('The Mobile field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, mobile, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superadmin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        user = self.create_user(email, mobile, password, **extra_fields)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField()
    mobile = models.CharField(max_length=15, unique=True)
    is_admin = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.email} ({self.mobile})"

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50 ,choices=[
        ('company', 'Company'),
        ('individual', 'Individual')
    ])

    def __str__(self):
        return f"{self.user.mobile} - {self.role}"

class CompanyDetails(models.Model):
    user_role = models.OneToOneField(UserRole, on_delete=models.CASCADE)
    company_name = models.CharField(editable=False)
    addressLine1 = models.CharField()
    addressLine2 = models.CharField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pin_no = models.CharField()
    alternate_phone_no = models.CharField()
    public_url_company = models.URLField()
    created_at = models.DateTimeField(default=timezone.now())
    updated_at = models.DateTimeField(auto_now=True)

class IndividualDetails(models.Model):
    user_role = models.OneToOneField(UserRole, on_delete=models.CASCADE)
    first_name = models.CharField(editable=False)
    last_name = models.CharField(editable=False)
    addressLine1 = models.CharField()
    addressLine2 = models.CharField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pin_code = models.BigIntegerField()
    alternate_phone_no = models.BigIntegerField()
    created_at = models.DateTimeField(default=timezone.now())
    updated_at = models.DateTimeField(auto_now=True)

class PanCardNos(models.Model):
    user_role = models.OneToOneField(UserRole, on_delete=models.CASCADE)
    pan_card_no = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now())

class BankAccountDetails(models.Model):
    user_role = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    account_number = models.BigIntegerField(unique=True)
    ifc_code = models.CharField(max_length=20)
    account_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now())

class Wallet(models.Model):
    user_role = models.OneToOneField(UserRole, on_delete=models.CASCADE,unique=True)
    primary_bankID = models.OneToOneField(BankAccountDetails,on_delete=models.CASCADE,unique=True)
    OutstandingBalance = models.FloatField()
    updated_at = models.DateTimeField() 

class Invoices(models.Model):
    invoice_id = models.CharField(max_length=10,unique=True,editable=False)
    primary_invoice_id = models.IntegerField(unique=True)
    product_name = models.CharField()
    principal_price = models.FloatField()
    interest = models.FloatField()
    xirr = models.FloatField()
    irr = models.FloatField()
    tenure_in_days = models.IntegerField()
    expiration_time = models.DateTimeField()
    is_fractionalized = models.BooleanField()
    expired = models.BooleanField(default=False)
    created_At = models.DateTimeField(default=timezone.now())

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            last_invoice = Invoices.objects.all().order_by('id').last()
            if last_invoice:
                last_id = int(last_invoice.invoice_id[1:])  # Extract the integer part of the last invoice_id
                new_id = last_id + 1
            else:
                new_id = 1
            self.invoice_id = f"I{new_id}"
        super(Invoices, self).save(*args, **kwargs)

    def __str__(self):
        return self.invoice_id

class FractionalUnits(models.Model):
    fractional_unit_id = models.CharField(max_length=20, unique=True, editable=False)
    invoice = models.ForeignKey(Invoices, on_delete=models.CASCADE)
    current_owner = models.ForeignKey(UserRole, on_delete=models.CASCADE, null=True, blank=True)
    sold = models.BooleanField(default=False)
    created_At = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.fractional_unit_id:
            last_unit = FractionalUnits.objects.filter(invoice=self.invoice).order_by('id').last()
            if last_unit:
                last_unit_id_str = last_unit.fractional_unit_id.split('-')[-1]
                last_unit_id = int(last_unit_id_str)
                new_unit_id = last_unit_id + 1
            else:
                new_unit_id = 1
            self.fractional_unit_id = f"{self.invoice.invoice_id}-{new_unit_id}"
        super(FractionalUnits, self).save(*args, **kwargs)

    def __str__(self):
        return self.fractional_unit_id

class AdminSettings(models.Model):
    interest_cut_off_time = models.TimeField(default=time(12, 0))

    def __str__(self):
        return f"Interest Cut Off Time: {self.interest_cut_off_time}"

# class SalePurchaseReport(models.Model):
#     unit = models.ForeignKey(FractionalUnits, on_delete=models.CASCADE)
#     seller = models.ForeignKey('Sellers', on_delete=models.CASCADE)
#     buyer = models.ForeignKey('Buyers', on_delete=models.CASCADE)
#     transaction_date = models.DateTimeField(auto_now_add=True)

class Configurations(models.Model):
    principal_price = models.FloatField()
    invoice_id = models.ForeignKey(Invoices,on_delete=models.CASCADE)
    user_id = models.ForeignKey(UserRole,on_delete=models.CASCADE)
    remaining_price = models.FloatField()

class Post_for_sale(models.Model):
  no_of_units = models.IntegerField()
  per_unit_price = models.FloatField()
  user_id = models.ForeignKey(UserRole,on_delete=models.CASCADE)
  invoice_id = models.ForeignKey(Invoices,on_delete=models.CASCADE)
  remaining_units = models.IntegerField()
  total_price = models.FloatField()
  withdrawn = models.BooleanField(default=False)
  post_time = models.TimeField(default=timezone.now())
  post_date = models.DateField(default=timezone.now())
  from_date = models.DateField()
  to_date = models.DateField()
  sold = models.BooleanField(default=False)
  post_dateTime = models.DateTimeField(default=timezone.now())
  configurationID = models.ForeignKey(Configurations,on_delete=models.CASCADE,null=True, blank=True)
  is_admin =  models.BooleanField()

class Buyers(models.Model):
    user_id = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    # invoice = models.ForeignKey(Invoices, on_delete=models.CASCADE)
    no_of_units = models.IntegerField()
    per_unit_price_invested = models.FloatField()
    # null=True,blank=True
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    purchase_date = models.DateField(default=timezone.now())
    purchase_time = models.TimeField(default=timezone.now())
    purchase_date_time = models.DateTimeField(default=timezone.now())

class Buyer_UnitsTracker(models.Model):
    buyer_id = models.ForeignKey(Buyers,on_delete=models.CASCADE)
    unitID = models.ForeignKey(FractionalUnits , on_delete=models.CASCADE)
    post_for_saleID = models.ForeignKey(Post_for_sale,on_delete=models.CASCADE,null=True,default=None)

class Sales(models.Model):
    UserID = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    Invoice = models.ForeignKey(Invoices , on_delete=models.CASCADE)
    no_of_units = models.IntegerField()
    sell_date = models.DateField(default=timezone.now())
    sell_time = models.TimeField(default=timezone.now())
    sell_date_time = models.DateTimeField(default=timezone.now())

class Post_For_Sale_UnitTracker(models.Model):
    unitID = models.ForeignKey(FractionalUnits,on_delete=models.CASCADE)
    post_for_saleID = models.ForeignKey(Post_for_sale, on_delete=models.CASCADE)
    sellersID = models.ForeignKey(Sales,on_delete=models.CASCADE,null=True,default=None)

class Sales_UnitTracker(models.Model):
    unitID = models.ForeignKey(FractionalUnits,on_delete=models.CASCADE)
    sellersID = models.ForeignKey(Sales,on_delete=models.CASCADE,null=True,default=None)

class WalletTransaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)
    type = models.CharField(max_length=50 , null=True)  # buy / sell
    creditedAmount = models.FloatField(null=True)
    debitedAmount = models.FloatField(null=True)
    status = models.CharField(max_length=50, choices=[('initiated', 'Initiated'), ('processing', 'Processing'), ('response', 'Response')])
    source = models.CharField(max_length=50, choices=[('bank_to_wallet', 'Bank to Wallet'), ('wallet_to_bank', 'Wallet to Bank'), ('wallet_to_buy', 'Wallet to Buy'), ('sell_to_wallet', 'Sell to Wallet')])
    purpose = models.CharField(max_length=255 , null=True)
    from_bank_acc = models.ForeignKey(BankAccountDetails, on_delete=models.CASCADE , null=True,related_name='from_bank_transactions')
    to_bank_acc = models.ForeignKey(BankAccountDetails, on_delete=models.CASCADE , null=True,related_name='to_bank_transactions')
    invoice = models.ForeignKey(Invoices, on_delete=models.CASCADE , null=True)
    time_date = models.DateTimeField()
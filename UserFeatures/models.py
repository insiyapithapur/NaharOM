from datetime import time, timezone
from django.utils import timezone
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager , PermissionsMixin
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, mobile, password=None, **extra_fields):
        """
        Create and return a regular user with an email, mobile, and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        if not mobile:
            raise ValueError(_('The Mobile field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, mobile, password=None, **extra_fields):
        """
        Create and return a superuser with an email, mobile, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, mobile, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile']

    def __str__(self):
        return f"{self.email} ({self.mobile})"
    
class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[('company', 'Company'), ('individual', 'Individual')])

class CompanyDetails(models.Model):
    user_role = models.OneToOneField(UserRole, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    company_address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pin_no = models.BigIntegerField()
    phone_no = models.BigIntegerField()
    company_pan_no = models.CharField(max_length=20)
    public_url_company = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class IndividualDetails(models.Model):
    user_role = models.OneToOneField(UserRole, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pin_code = models.BigIntegerField()
    phone_no = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PanCardNos(models.Model):
    user_role = models.OneToOneField(UserRole, on_delete=models.CASCADE)
    pan_card_no = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

class BankAccountDetails(models.Model):
    user_role = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    account_number = models.BigIntegerField(unique=True)
    ifc_code = models.CharField(max_length=20)
    account_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class OutstandingBalance(models.Model):
    bank_acc = models.OneToOneField(BankAccountDetails, on_delete=models.CASCADE)
    balance = models.FloatField()
    updated_at = models.DateField() #updated DateTime

class Invoices(models.Model):
    primary_invoice_id = models.IntegerField()
    no_of_partitions = models.IntegerField()
    name = models.CharField(max_length=255)
    post_date = models.DateField()
    post_time = models.TimeField()
    post_date_time = models.DateTimeField()
    interest = models.FloatField()
    xirr = models.FloatField()
    irr = models.FloatField()
    tenure_in_days = models.IntegerField()
    principle_amt = models.IntegerField()
    expiration_time = models.DateTimeField(default=time(12, 0))
    remaining_partitions = models.IntegerField(null=True , blank=True)
    sold = models.BooleanField(default=False)

class FractionalUnits(models.Model):
    invoice = models.ForeignKey(Invoices, on_delete=models.CASCADE)
    unit_id = models.UUIDField(default=uuid.uuid4, unique=True)
    current_owner = models.ForeignKey(UserRole, on_delete=models.CASCADE , null=True, blank=True)
    sold = models.BooleanField(default=False)

class AdminSettings(models.Model):
    interest_cut_off_time = models.TimeField(default=time(12, 0))

    def __str__(self):
        return f"Interest Cut Off Time: {self.interest_cut_off_time}"

class SalePurchaseReport(models.Model):
    unit = models.ForeignKey(FractionalUnits, on_delete=models.CASCADE)
    seller = models.ForeignKey('Sellers', on_delete=models.CASCADE)
    buyer = models.ForeignKey('Buyers', on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(auto_now_add=True)

class Buyers(models.Model):
    user = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoices, on_delete=models.CASCADE)
    no_of_partitions = models.IntegerField()
    total_amount_invested = models.FloatField()
    # null=True,blank=True
    wallet = models.ForeignKey('OutstandingBalance', on_delete=models.CASCADE)
    purchase_date = models.DateField()
    purchase_time = models.TimeField()
    purchase_date_time = models.DateTimeField(default=timezone.now())

class Sellers(models.Model):
    User = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    Invoice = models.ForeignKey(Invoices , on_delete=models.CASCADE)
    amount = models.FloatField()
    wallet = models.ForeignKey('OutstandingBalance', on_delete=models.CASCADE)
    no_of_partitions = models.IntegerField()
    sell_date = models.DateField()
    sell_time = models.TimeField()
    sell_date_time = models.DateTimeField(default=timezone.now())
    remaining_partitions = models.IntegerField()
    sold = models.BooleanField(default=False)

class OutstandingBalanceTransaction(models.Model):
    wallet = models.ForeignKey(OutstandingBalance, on_delete=models.CASCADE)
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)
    type = models.CharField(max_length=50 , null=True)  # buy / sell
    creditedAmount = models.FloatField(null=True)
    debitedAmount = models.FloatField(null=True)
    status = models.CharField(max_length=50, choices=[('initiated', 'Initiated'), ('processing', 'Processing'), ('response', 'Response')])
    source = models.CharField(max_length=50, choices=[('bank_to_wallet', 'Bank to Wallet'), ('wallet_to_bank', 'Wallet to Bank'), ('wallet_to_buy', 'Wallet to Buy'), ('sell_to_wallet', 'Sell to Wallet')])
    purpose = models.CharField(max_length=255 , null=True)
    bank_acc = models.ForeignKey(BankAccountDetails, on_delete=models.CASCADE , null=True)
    invoice = models.ForeignKey(Invoices, on_delete=models.CASCADE , null=True)
    time_date = models.DateTimeField()
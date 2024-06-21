from django.db import models
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager , PermissionsMixin
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser , PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    password = models.CharField(max_length=128)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class SecurityQuestion(models.Model):
    question = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.question

class UserRole(models.Model):
    ROLE_CHOICES = [
        ('company', 'Company'),
        ('individual', 'Individual'),
        # ('admin' , 'Admin')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    registration = models.BooleanField(default=False)
    user_profile = models.BooleanField(default=False)
    CheckBankAccountDetails = models.BooleanField(default=False)
    CheckPanCardNo = models.BooleanField(default=False)
    CheckFunds = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.email} - {self.role}"

class CompanyDetails(models.Model):
    user_role = models.OneToOneField(UserRole, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    company_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_no = models.BigIntegerField()
    phone_no = models.BigIntegerField()
    company_pan_no = models.CharField(max_length=50)
    public_url_company = models.URLField()
    security_question = models.ForeignKey(SecurityQuestion, on_delete=models.CASCADE)
    security_question_ans = models.CharField(max_length=255)

    def __str__(self):
        return self.company_name

class IndividualDetails(models.Model):
    user_role = models.OneToOneField(UserRole, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.BigIntegerField()
    phone_no = models.BigIntegerField()
    security_question = models.ForeignKey(SecurityQuestion, on_delete=models.CASCADE)
    security_question_ans = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class PanCardNos(models.Model):
    user_role = models.OneToOneField(UserRole, on_delete=models.CASCADE)
    pan_card_no = models.CharField(max_length=50)

    def __str__(self):
        return self.pan_card_no

class BankAccountDetails(models.Model):
    user_role = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    account_number = models.BigIntegerField(unique=True)
    ifc_code = models.CharField(max_length=11)
    account_type = models.CharField(max_length=50)

    def __str__(self):
        return str(self.account_number)

class Wallet(models.Model):
    bank_acc = models.OneToOneField(BankAccountDetails, on_delete=models.CASCADE)
    balance = models.FloatField()
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"Wallet for {self.bank_acc.account_number}"
    
class Invoices(models.Model):
    primary_invoice_id = models.IntegerField()
    no_of_fractional_Unit = models.IntegerField()
    Discounting = models.FloatField()
    company_description = models.TextField()
    networth_of_company = models.FloatField()
    name = models.CharField(max_length=255)
    InvoiceTotalPrice = models.FloatField()
    SomeonePurchase = models.BooleanField(default=False)
    PostDate  = models.DateField()
    PostTime = models.TimeField()

    def __str__(self):
        return str(self.primary_invoice_id)

class Buyer(models.Model):
    invoice = models.ForeignKey(Invoices, on_delete=models.CASCADE)
    user = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    no_of_Fractional_Unit = models.IntegerField()
    total_amount_invested = models.FloatField()
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    post_for_sell = models.BooleanField(default=False)
    Someone_purchase = models.BooleanField(default=False)
    purchaseDate = models.DateField()
    purchaseTime = models.TimeField()

    def __str__(self):
        return str(self.invoice , " " , self.user , " " , self.no_of_Fractional_Unit , " ", self.purchaseDate)

class Seller(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    amount = models.FloatField()
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    SellDate = models.DateField()
    SellTime = models.TimeField()

    def __str__(self):
        return str(self.buyer , " " , self.SellDate)

class WalletTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('bank_to_wallet', 'Bank to Wallet'),
        ('wallet_to_bank', 'Wallet to Bank'),
        ('wallet_to_buy', 'Wallet to Buy'),
        ('sell_to_wallet', 'Sell to Wallet'),
    )
    STATUS_CHOICES = (
        ('initiated', 'Initiated'),
        ('processing', 'Processing'),
        ('response', 'Response'),
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    credited = models.BooleanField()
    debited = models.BooleanField()
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    transaction_type = models.CharField(max_length=255, choices=TRANSACTION_TYPE_CHOICES)
    bankAcc = models.ForeignKey(BankAccountDetails, on_delete=models.SET_NULL, null=True, blank=True)
    invoice = models.ForeignKey(Invoices, on_delete=models.SET_NULL, null=True, blank=True)
    timeDate = models.DateTimeField(auto_now_add=True)
from datetime import datetime
import os
from django.utils import timezone
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from UserFeatures import models
from django.utils import timezone
from django.db import transaction
import base64
import time
from django.conf import settings
import hashlib
from django.db.models import Q

@csrf_exempt
def ExtractInvoicesAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            if not isinstance(data, list):
                return JsonResponse({"message": "Invalid input format, expected a list of objects"}, status=400)

            filtered_invoices = []

            for company in data:
                invoices = company.get('invoices', [])
                for invoice in invoices:
                    if invoice.get('product') is not None:
                        filtered_invoices.append(invoice)
            
            return JsonResponse({"filtered_invoices": filtered_invoices}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only POST methods are allowed"}, status=405)

with open(os.path.join(os.path.dirname(__file__), 'invoices.json')) as f:
    invoices_data = json.load(f)

def filter_invoice_data(invoice):
    product = invoice.get('product', {})
    # print("product: ",product)
    return {
        "primary_invoice_id": invoice['id'],
        # hyperlink attach karvani che j dashboard open kare invoice no primary mathi
        "buyer_poc_name" : invoice['buyer_poc_name'],
        "product_name": product.get('name'),
        "irr": product.get('interest_rate_fixed'),
        "tenure_in_days": product.get('tenure_in_days'),
        "interest_rate" : product.get('interest'),
        "xirr" : product.get('xirr_in_percentage'),
        "principle_amt" : product.get('principle_amt'),
        "expiration_time" : timezone.now() + timezone.timedelta(days=product.get('tenure_in_days'))
    }

@csrf_exempt
def GetInvoicesAPI(request, user_id, primary_invoice_id=None):
    if request.method == 'GET':
        try:
            if not user_id:
                return JsonResponse({"message": "user_id is required"}, status=400)

            try:
                user = models.User.objects.get(id=user_id)
            except models.User.DoesNotExist:
                return JsonResponse({"message": "User not found"}, status=404)

            if not user.is_admin:
                return JsonResponse({"message": "For this operation you have to register yourself with admin role"}, status=403)

            if primary_invoice_id:
                invoice_data = next((inv for inv in invoices_data['filtered_invoices'] if inv['id'] == primary_invoice_id), None)
                if not invoice_data:
                    return JsonResponse({"message": "Invoice not found"}, status=404)
                filtered_invoice_data = filter_invoice_data(invoice_data)
                return JsonResponse(filtered_invoice_data, status=200)
            else:
                filtered_invoices_data = [filter_invoice_data(inv) for inv in invoices_data['filtered_invoices']]
                return JsonResponse(filtered_invoices_data, safe=False, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET methods are allowed"}, status=405)
    
@csrf_exempt
def InvoiceMgtAPI(request,user, primary_invoice_id=None):
    if request.method == 'GET':
        try:
            try:
                user_role = models.UserRole.objects.get(id=user)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User not found"}, status=404)
            
            if not user_role.user.is_admin:
                return JsonResponse({"message": "For this operation you have to register yourself with admin role"}, status=403)

            if primary_invoice_id:
                invoice_data = next((inv for inv in invoices_data['filtered_invoices'] if inv['id'] == primary_invoice_id), None)
                if not invoice_data:
                    return JsonResponse({"message": "Invoice not found"}, status=404)
                filtered_invoice_data = filter_invoice_data(invoice_data)
                return JsonResponse(filtered_invoice_data, status=200)
            else:
                configured_invoices = models.Configurations.objects.filter(remaining_units__gt=0)
                configured_invoices_data = []
                for configured_invoice in configured_invoices:
                    configured_invoice = {
                        "id" : configured_invoice.invoice_id.id,
                        "invoice_id" : configured_invoice.invoice_id.invoice_id,
                        "primary_invoice_id": configured_invoice.invoice_id.primary_invoice_id,
                        'configured_ID' : configured_invoice.id,
                    #    hyperlink attach karvani che j dashboard open kare invoice no primary mathi
                        "product_name": configured_invoice.invoice_id.product_name,
                        "irr": configured_invoice.invoice_id.irr,
                        "tenure_in_days": configured_invoice.invoice_id.tenure_in_days,
                        "interest_rate" : configured_invoice.invoice_id.interest,
                        "xirr" : configured_invoice.invoice_id.xirr,
                        "expiration_time" : configured_invoice.invoice_id.expiration_time,
                        'principle_amt' : configured_invoice.principal_price ,
                        'per_unit_price' : configured_invoice.per_unit_price,
                        'no_of_units' : configured_invoice.no_of_units ,
                        'user_id' : configured_invoice.user_id.id,
                        'remaining_units' : configured_invoice.remaining_units,
                        "type" : "configured",
                    }
                    configured_invoices_data.append(configured_invoice)
                print(configured_invoices)
                check_configured_invoices = models.Configurations.objects.all()
                configured_invoice_ids = {inv.invoice_id.primary_invoice_id for inv in check_configured_invoices}

                unfractionalized_invoices = [filter_invoice_data(inv) for inv in invoices_data['filtered_invoices']]
                unfractionalized_invoices_data = []

                for unfractionalized_invoice in unfractionalized_invoices:
                    if unfractionalized_invoice['primary_invoice_id'] not in configured_invoice_ids:
                        unfractionalized_data = {
                            "primary_invoice_id": unfractionalized_invoice['primary_invoice_id'],
                            # hyperlink attach karvani che j dashboard open kare invoice no primary mathi
                            "buyer_poc_name" : unfractionalized_invoice['buyer_poc_name'],
                            "product_name": unfractionalized_invoice['product_name'],
                            "irr": unfractionalized_invoice['irr'],
                            "tenure_in_days": unfractionalized_invoice['tenure_in_days'],
                            "interest_rate" : unfractionalized_invoice['interest_rate'],
                            "xirr" : unfractionalized_invoice['xirr'],
                            "principle_amt" : unfractionalized_invoice['principle_amt'],
                            "remaining_amt" : unfractionalized_invoice['principle_amt'],
                            "expiration_time" : unfractionalized_invoice['expiration_time'],
                            "type" : "unfractionalized"
                        }
                        unfractionalized_invoices_data.append(unfractionalized_data)
                print("unfractionalized_invoices_data : ",unfractionalized_invoices_data)
                   
                fractionalized_invoice_data = models.Post_for_sale.objects.filter(
                    configurationID__isnull = False
                )
                print("fractionalized_invoice_data : ",fractionalized_invoice_data)
                response_data = []
                for post in fractionalized_invoice_data:
                    invoice = post.invoice_id
                    configuration = post.configurationID
                    post_data = {
                        'id' : invoice.id,
                        'invoice_id' : invoice.invoice_id,
                        'primary_invoice_id' : invoice.primary_invoice_id,
                        'post_for_saleID': post.id,
                        'configurationID' : configuration.id ,
                        'product_name' : invoice.product_name,
                        'interest' : invoice.interest,
                        'xirr' : invoice.xirr,
                        'irr' : invoice.irr,
                        'tenure_in_days' : invoice.tenure_in_days ,
                        'expiration_time' : invoice.expiration_time ,
                        'expired' : invoice.expired ,
                        'no_of_units': post.no_of_units,
                        'per_unit_price': post.per_unit_price,
                        'total_price' : post.total_price,
                        'userID' : post.user_id.id ,
                        'remaining_units' : post.remaining_units,
                        'withdrawn' : post.withdrawn,
                        'post_time' : post.post_time ,
                        'post_date' : post.post_date ,
                        'from_date' : post.from_date ,
                        'to_date'  : post.to_date ,
                        'type': 'fractionalized'
                    }
                    print("post : ",post)
                    response_data.append(post_data)

                all_data = response_data + configured_invoices_data + unfractionalized_invoices_data
                    
                return JsonResponse({"user": user_role.id, "data": all_data}, safe=False, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only POST methods are allowed"}, status=405)

@csrf_exempt
def ConfigurationAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = data.get('user')
            primary_invoice_id = data.get('primary_invoice_id')
            no_of_units = data.get('no_of_units')
            per_unit_price = data.get('per_unit_price')

            try:
                user_role = models.UserRole.objects.get(id=user)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User not found"}, status=404)
            
            if not user_role.user.is_admin:
                return JsonResponse({"message": "For this operation you have to register yourself with admin role","user":user_role.id}, status=403)

            invoice_data = next((inv for inv in invoices_data['filtered_invoices'] if inv['id'] == primary_invoice_id), None)
            if not invoice_data or not invoice_data.get('product'):
                return JsonResponse({"message": "Invoice data not found or product is null","user":user_role.id}, status=404)
            with transaction.atomic():
                try :
                    invoice = models.Invoices.objects.get(primary_invoice_id=primary_invoice_id)
                    return JsonResponse({"message":"Configuration of this invoice is already done","invoiceID":invoice.id,"user":user_role.id},status=200)
                except models.Invoices.DoesNotExist:
                    product_data = invoice_data['product']
                    product_name = product_data['name']
                    principal_price = product_data['principle_amt']
                    interest = product_data['interest']
                    xirr = product_data['xirr_in_percentage']
                    irr = product_data['interest_rate_fixed']
                    tenure_in_days = product_data['tenure_in_days']
                    expiration_time = timezone.now() + timezone.timedelta(days=tenure_in_days)

                    invoice = models.Invoices.objects.create(
                            primary_invoice_id = primary_invoice_id ,
                            product_name = product_name ,
                            principal_price = principal_price ,
                            interest = interest ,
                            xirr = xirr ,
                            irr = irr ,
                            tenure_in_days = tenure_in_days ,
                            expiration_time = expiration_time ,
                            expired = False ,
                            created_At = timezone.now()
                        )
                    
                    configure = models.Configurations.objects.create(
                        principal_price = principal_price,
                        per_unit_price = per_unit_price,
                        no_of_units = no_of_units ,
                        invoice_id = invoice,
                        user_id = user_role,
                        remaining_units = no_of_units
                        ) 
                    
                    for _ in range(no_of_units):
                        fractional_unit = models.FractionalUnits.objects.create(
                                invoice = invoice,
                                current_owner = None,
                                posted_for_sale = False,
                                configurationID = configure,
                                created_At = timezone.now()
                            )
                    return JsonResponse({"message": "Successfully configured ","invoice" : invoice.id , "configured" : configure.id ,"user":user_role.id}, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only POST methods are allowed"}, status=405)

@csrf_exempt
def PostInvoiceAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user')
            no_of_units = data.get('no_of_units')
            per_unit_price = data.get('per_unit_price')
            from_date = data.get('from_date')
            to_date = data.get('to_date')
            total_price = data.get('total_price')
            configureID = data.get('configureID')

            try:
                user_role = models.UserRole.objects.get(id=user_id)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message":"user does not exist"},status=400)
            
            if not user_role.user.is_admin:
                return JsonResponse({"message":"For this operation you have to be admin","user":user_role.id},status=400)
    
            with transaction.atomic():
                try:
                    configure = models.Configurations.objects.get(id=configureID)  
                    if configure.remaining_units < no_of_units:
                        return JsonResponse({"message" : "Not sufficient units for selling","user":user_role.id},status=400)
                    post_for_sale = models.Post_for_sale.objects.create(
                        no_of_units = no_of_units ,
                        per_unit_price = per_unit_price ,
                        user_id = user_role ,
                        invoice_id = configure.invoice_id ,
                        total_price = total_price,
                        remaining_units = no_of_units ,
                        withdrawn = False ,
                        post_time = timezone.now().time() ,
                        post_date = timezone.now().date(),
                        from_date = from_date ,
                        to_date = to_date ,
                        post_dateTime = timezone.now() ,
                        configurationID = configure ,
                        is_admin =  user_role.user.is_admin
                    )
                    fractional_units = models.FractionalUnits.objects.filter(
                        posted_for_sale=False,
                        invoice=configure.invoice_id,
                        configurationID=configure,
                        current_owner__isnull=True
                    )[:no_of_units]

                    if fractional_units.count() < no_of_units:
                        return JsonResponse({"message": "Not enough fractional units available"}, status=400)

                    for unit in fractional_units:
                        models.Post_For_Sale_UnitTracker.objects.create(
                            unitID=unit,
                            post_for_saleID=post_for_sale,
                            sellersID=None  
                        )
                        unit.posted_for_sale = True
                        unit.save()

                    configure.remaining_units -= no_of_units
                    configure.save()
                    return JsonResponse({"message": "Successfully posted for sale", "posted_for_saleID": post_for_sale.id , 'invoice_id' : post_for_sale.invoice_id.id,"user":user_role.id}, status=201)
                except models.Configurations.DoesNotExist:
                    return JsonResponse({"message":"Configuration does not exist" , "user":user_role.id},status=400)   
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only POST methods are allowed"}, status=405)
    
@csrf_exempt
def UserManagementAPI(request,user):
    if request.method == 'GET':
        try:
            user_is_admin = models.UserRole.objects.get(id=user)

            if not user_is_admin.user.is_admin:
                return JsonResponse({"message" : "For this operation you should be admin or superadmin"},status=500)
            
            if not user_is_admin.user.is_superadmin:
                return JsonResponse({"message" : "For this operation you should be admin or superadmin"},status=500)
            
            user_roles = models.UserRole.objects.all()
            all_user_details = []

            for user_role in user_roles:
                try:
                    user_details = {
                        "user": user_role.id,
                        "user_role": user_role.role,
                        "email": user_role.user.email,
                        "mobile" : user_role.user.mobile ,
                        "date_of_joining": user_role.user.created_at,
                    }

                    if user_role.role == 'Company':
                        try : 
                            company_details = models.CompanyDetails.objects.get(user_role=user_role)
                            user_details.update({
                                "company_name": company_details.company_name,
                                # "company_name": "ABC",
                            })
                        except models.CompanyDetails.DoesNotExist:
                            user_details.update({
                                "company_name": None,
                                # "company_name": "ABC",
                            })
                    elif user_role.role == 'Individual':
                        try :
                            individual_details = models.IndividualDetails.objects.get(user_role=user_role)
                            user_details.update({
                                "first_name": individual_details.first_name,
                                "last_name": individual_details.last_name,
                                # "first_name": "First name",
                                # "last_name": "last name",
                            })
                        except models.IndividualDetails.DoesNotExist:
                            user_details.update({
                                "first_name": None,
                                "last_name": None,
                                # "first_name": "First name",
                                # "last_name": "last name",
                            })
                    try:
                        pan_card = models.PanCardNos.objects.get(user_role=user_role)
                        user_details["pan_card_no"] = pan_card.pan_card_no
                    except models.PanCardNos.DoesNotExist:
                        user_details["pan_card_no"] = None

                    # permissions = {s
                    #     "is_admin": user.is_admin,
                    #     "is_staff": user.is_staff,
                    #     "is_active": user.is_active
                    # }
                    user_details["is_admin"] = user_role.user.is_admin
                    user_details["is_superadmin"] = user_role.user.is_superadmin

                    all_user_details.append(user_details)

                except models.UserRole.DoesNotExist:
                    return JsonResponse({"message" : "UserRole does not exist"},status=400)
                except Exception as e :
                    return JsonResponse({"message":str(e)},status=500)
            return JsonResponse(all_user_details, safe=False ,status=200)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET methods are allowed"}, status=405)

@csrf_exempt
def usersLedgerAPI(request, user):
    if request.method == 'GET':
        try:
            user_is_admin = models.UserRole.objects.get(id=user)

            if not user_is_admin.user.is_admin and not user_is_admin.user.is_superadmin:
                return JsonResponse({"message": "For this operation you should be admin or superadmin"}, status=500)

            user_roles = models.UserRole.objects.exclude(Q(user__is_admin=True) | Q(user__is_superadmin=True))

            response_data = []

            for user_role in user_roles:
                user_data = {
                    "user": user_role.id,
                    "role": user_role.role,
                    "mobile": user_role.user.mobile,
                    "email": user_role.user.email,
                    "bank_Accounts": [],
                    "wallet_balance": None,
                    "wallet_transaction": []
                }

                try:
                    bankAccs = models.BankAccountDetails.objects.filter(user_role=user_role)
                    user_data["bank_Accounts"] = [
                        {
                            "user": user_role.id,
                            "bankAcc_ID": bankAcc.id,
                            "account_number": bankAcc.account_number,
                            "ifc_code": bankAcc.ifc_code,
                            "account_type": bankAcc.account_type
                        }
                        for bankAcc in bankAccs
                    ]

                    wallet = models.Wallet.objects.get(user_role=user_role)
                    user_data["wallet_balance"] = wallet.OutstandingBalance
                    user_data["primary_bankAcc_ID"] = wallet.primary_bankID.id
                    wallet_transactions = models.WalletTransaction.objects.filter(wallet=wallet)
                    user_data["wallet_transaction"] = [
                        {
                            "user": wallet_transaction.wallet.primary_bankID.user_role.id,
                            "walletID": wallet_transaction.wallet.id,
                            "transaction_id": wallet_transaction.transaction_id,
                            "type": wallet_transaction.type,
                            "creditedAmount": wallet_transaction.creditedAmount,
                            "debitedAmount": wallet_transaction.debitedAmount,
                            "status": wallet_transaction.status,
                            "source": wallet_transaction.source,
                            "purpose": wallet_transaction.purpose,
                            "from_bank_acc": wallet_transaction.from_bank_acc.account_number if wallet_transaction.from_bank_acc else None,
                            "from_user": wallet_transaction.from_bank_acc.user_role.id if wallet_transaction.from_bank_acc else None,
                            "to_bank_acc": wallet_transaction.to_bank_acc.account_number if wallet_transaction.to_bank_acc else None,
                            "to_user": wallet_transaction.to_bank_acc.user_role.id if wallet_transaction.to_bank_acc else None,
                            "invoice": wallet_transaction.invoice.invoice_id if wallet_transaction.invoice else None,
                            "time_date": wallet_transaction.time_date
                        }
                        for wallet_transaction in wallet_transactions
                    ]

                except models.BankAccountDetails.DoesNotExist:
                    pass  
                except models.Wallet.DoesNotExist:
                    pass  
                except models.WalletTransaction.DoesNotExist:
                    pass  

                response_data.append(user_data)

            return JsonResponse(response_data, safe=False, status=200)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET methods are allowed"}, status=405)

@csrf_exempt
def SalesPurchasedReportAPI(request,user):
    if request.method == 'GET':
        try:
            if not user:
                return JsonResponse({"message": "user ID is required"}, status=400)
            
            try:
                user_role = models.UserRole.objects.get(id=user)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User not found"}, status=404)

            if not user_role.user.is_admin:
                return JsonResponse({"message": "For this operation you have to register yourself with admin role"}, status=403)
            
            with transaction.atomic():
                try:
                    sales_purchase_reports = models.SalePurchaseReport.objects.all()
                    report_list = []
                    for report in sales_purchase_reports:
                        if report.seller_ID.role == 'Individual' :
                            try :
                                seller_profile = models.IndividualDetails.objects.get(user_role=report.seller_ID)
                                Seller_Name = seller_profile.first_name
                            except models.IndividualDetails.DoesNotExist:
                                Seller_Name = None
                        else :
                            try :
                                seller_profile = models.CompanyDetails.objects.get(user_role=report.seller_ID)
                                Seller_Name = seller_profile.company_name
                            except models.CompanyDetails.DoesNotExist:
                                Seller_Name = None
                        
                        if report.buyerID_ID.role == 'Individual' :
                            try :
                                buyer_profile = models.IndividualDetails.objects.get(user_role=report.buyerID_ID)
                                Buyer_Name = buyer_profile.first_name
                            except models.IndividualDetails.DoesNotExist:
                                Buyer_Name = None
                        else :
                            try :
                                buyer_profile = models.CompanyDetails.objects.get(user_role=report.buyerID_ID)
                                Buyer_Name = buyer_profile.company_name
                            except models.CompanyDetails.DoesNotExist:
                                Buyer_Name = None

                        try :
                            seller_pancard = models.PanCardNos.objects.get(user_role=report.seller_ID)
                            Seller_PAN = seller_pancard.pan_card_no
                        except models.PanCardNos.DoesNotExist:
                            Seller_PAN = None
                        
                        try :
                            buyer_pancard = models.PanCardNos.objects.get(user_role=report.buyerID_ID)
                            Buyer_PAN = buyer_pancard.pan_card_no
                        except models.PanCardNos.DoesNotExist:
                            Buyer_PAN = seller_profile.first_name

                        report_data = {
                            'id': report.id,
                            'invoiceID' : report.invoiceID.invoice_id,
                            'unitID' : report.unitID.fractional_unit_id,
                            'Listing_Date' : report.ListingDate,
                            'Seller_ID' : report.seller_ID.id,
                            'Seller_Name' : Seller_Name,
                            'Seller_PAN' : Seller_PAN,
                            'Sale_Buy_Date' : report.Sale_Buy_Date,
                            'Sale_Buy_per_unit_price' : report.Sale_Buy_per_unit_price,
                            'Buyer_ID' : report.buyerID_ID.id ,
                            'Buyer_Name' : Buyer_Name,
                            'Buyer_PAN' : Buyer_PAN,
                            'no_of_days_units_held' : report.no_of_days_units_held,
                            'interest_due_to_seller' : report.interest_due_to_seller,
                            'TDS_deducted' : report.TDS_deducted,
                            'IRR' : report.IRR  
                        }
                        report_list.append(report_data)

                    return JsonResponse({"sales_purchase_reports": report_list,"user":user_role.id}, status=200)

                except models.SalePurchaseReport.DoesNotExist:
                    return JsonResponse({"message": "SalePurchaseReport not found"}, status=404)
                # return JsonResponse({"sales_purchase_report" : sales_purchase_report},status=200)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET methods are allowed"}, status=405)
    
def generate_token(admin_id, user_role_id):
    timestamp = int(time.time())
    token = f"{admin_id}:{user_role_id}:{timestamp}"
    signature = hashlib.sha256(f"{token}:{settings.SECRET_KEY}".encode()).hexdigest()
    token_with_signature = f"{token}:{signature}"
    encoded_token = base64.urlsafe_b64encode(token_with_signature.encode()).decode()
    return encoded_token

def decode_token(token):
    try:
        decoded_token = base64.urlsafe_b64decode(token.encode()).decode()
        parts = decoded_token.split(':')
        if len(parts) != 4:
            return None
        
        admin_id, user_role_id, timestamp, received_signature = parts
        token_without_signature = f"{admin_id}:{user_role_id}:{timestamp}"
        expected_signature = hashlib.sha256(f"{token_without_signature}:{settings.SECRET_KEY}".encode()).hexdigest()
        
        if received_signature != expected_signature:
            return "token is invalid"
        
        return admin_id, user_role_id, int(timestamp)
    except Exception as e:
        return "failed to decode the token"
    
@csrf_exempt
def GenerateTokenAPI(request, admin_id, user_role_id):
    if request.method == 'GET':
        try:
            admin = models.User.objects.get(id=admin_id, is_superadmin=True)
        except models.User.DoesNotExist:
            return JsonResponse({"message": "Admin not found or not authorized"}, status=404)

        try:
            user = models.UserRole.objects.get(id=user_role_id)
        except models.UserRole.DoesNotExist:
            return JsonResponse({"message": "User not found"}, status=404)
        
        token = generate_token(admin_id, user_role_id)
        return JsonResponse({"token": token}, status=200)
    else:
        return JsonResponse({"message": "Only GET methods are allowed"}, status=405)
    
@csrf_exempt
def UserPersonateAPI(request,token):
    if request.method == 'GET':
        if not token:
            return JsonResponse({"message": "Token is required"}, status=400)

        decoded_data = decode_token(token)
        if not decoded_data:
            return JsonResponse({"message": "Invalid token"}, status=400)

        admin_id, user_role_id, timestamp = decoded_data

        try:
            admin = models.User.objects.get(id=admin_id, is_superadmin=True)
        except models.User.DoesNotExist:
            return JsonResponse({"message": "Admin not found or not authorized"}, status=403)

        try:
            user_role = models.UserRole.objects.get(id=user_role_id)
        except models.UserRole.DoesNotExist:
            return JsonResponse({"message": "User not found"}, status=404)

        user_dashboard_data = {
            "user_role": user_role.id,
            "user_email": user_role.user.email,
        }
        return JsonResponse(user_dashboard_data, status=200)
    else:
        return JsonResponse({"message": "Only GET methods are allowed"}, status=405)
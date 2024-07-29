import uuid
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json 
from django.http import JsonResponse
from . import models
from django.utils import timezone
from django.db import transaction
from django.utils.dateparse import parse_time
import requests
from django.db.models import Q

@csrf_exempt
def RegisterAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mobile = data.get('mobile')
            role = data.get('role')

            if not mobile or not role:
                return JsonResponse({"message": "Mobile and role are required"}, status=400)

            try:
                user = models.User.objects.get(mobile = mobile)
                user_role = models.UserRole.objects.get(user = user , role = role)
                return JsonResponse({"message": "User already exist"}, status=400)
            except models.UserRole.DoesNotExist:
                #  api integrate , mobile --> email
                user = models.User.objects.create(
                    mobile=mobile,
                    email="default8141@gmail.com"
                )
                user_role = models.UserRole.objects.create(
                    user=user,
                    role=role
                )

                return JsonResponse({
                    "message": "User registered successfully",
                    "user_role_id": user_role.id
                }, status=201)
            
            # existing_roles = models.UserRole.objects.filter(user=user).values_list('role', flat=True)
            # if role in existing_roles:
            #     return JsonResponse({"message": f"User already registered with role '{role}'"}, status=400)
            
            # if 'company' in existing_roles and 'individual' in existing_roles:
            #     return JsonResponse({"message": "Already created both roles for this email"}, status=400)

            # user_role = models.UserRole.objects.create(
            #     user=user,
            #     role=role
            # )
            # return JsonResponse({"message": "Role added to existing user", "user_role_id": user_role.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)
    
@csrf_exempt
def LoginAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mobile = data.get('mobile')
            role = data.get('role')

            if not mobile or not role:
                return JsonResponse({"message": "Email, password, and role are required"}, status=400)

            try:
                user = models.User.objects.get(mobile=mobile)
                print(user)
                if user:
                    try:
                        user_role = models.UserRole.objects.get(user=user, role=role)
                        return JsonResponse({"message": "Login successful", "user_role_id": user_role.id}, status=200)
                    except models.UserRole.DoesNotExist:
                        return JsonResponse({"message": "Role mismatch for the given email"}, status=400)
                else:
                    return JsonResponse({"message": "Invalid email or password"}, status=401)
            except models.User.DoesNotExist:
                return JsonResponse({"message": "Email doesn't exist"}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)

# @csrf_exempt
# def ChangeStatusAPI(request):
#     if request.method == 'GET':
           
@csrf_exempt
def BankAccDetailsAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_role_id = data.get('user_role_id')

            if not user_role_id:
                return JsonResponse({"message": "user_role_id is required"}, status=400)

            try:
                user_role = models.UserRole.objects.get(id=user_role_id)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found"}, status=404)

            try:
                # following details will come from 3rd party api
                account_number = data.get('account_number')
                ifc_code = data.get('ifc_code')
                account_type = data.get('account_type')
                print(account_number , ifc_code , account_type)

                if not account_number or not ifc_code or not account_type:
                    return JsonResponse({"message": "account_number, ifc_code, and account_type are required"}, status=400)

                if models.BankAccountDetails.objects.filter(user_role=user_role, account_number=account_number).exists():
                    return JsonResponse({"message": "Already there account no."}, status=400)

                bank_account_details = models.BankAccountDetails.objects.create(
                    user_role=user_role,
                    account_number=account_number,
                    ifc_code=ifc_code,
                    account_type=account_type
                )

                return JsonResponse({"message": "Bank account details saved successfully", "bank_account_id": bank_account_details.id}, status=201)

            except KeyError:
                return JsonResponse({"message": "Missing required fields"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

    elif request.method == 'GET':
        try:
            data = json.loads(request.body)
            user_role_id = data.get('user_role_id')
            print(user_role_id)

            if not user_role_id:
                return JsonResponse({"message": "user_role_id is required"}, status=400)

            try:
                user_role = models.UserRole.objects.get(id=user_role_id)
                print(user_role)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found"}, status=404)

            bank_accounts = models.BankAccountDetails.objects.filter(user_role=user_role)
            print(bank_accounts.count())
            if not bank_accounts.exists():
                return JsonResponse({"message": "No bank accounts found for this user role"}, status=404)

            account_numbers = [{"bank_account_id": acc.id, "account number ending with": str(acc.account_number)[-4:]} for acc in bank_accounts]
            return JsonResponse({"bank_accounts": account_numbers}, status=200)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    else:
        return JsonResponse({"message": "Only POST and GET methods are allowed"}, status=405)

@csrf_exempt
def Credit_FundsAPI(request):
    if request.method == 'POST':
        print("after post")
        try:
            data = json.loads(request.body)
            user_role_id = data.get('user_role_id')
            bank_acc_id = data.get('bank_acc_id')
            amount = data.get('amount')

            if not user_role_id or not bank_acc_id or not amount:
                return JsonResponse({"message": "user_role_id, bank_acc_id, and amount are required"}, status=400)

            try:
                user_role = models.UserRole.objects.get(id=user_role_id)
                print(user_role)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found"}, status=404)

            try:
                bank_account = models.BankAccountDetails.objects.get(id=bank_acc_id, user_role=user_role)
                print(bank_account)
            except models.BankAccountDetails.DoesNotExist:
                return JsonResponse({"message": "Bank account not found for the given user role"}, status=404)

            try:
                print("in try")
                wallet = models.OutstandingBalance.objects.get(bank_acc=bank_account)
                print(wallet)
                wallet.balance += amount
                wallet.updated_at = timezone.now().date()
                wallet.save()
            except models.OutstandingBalance.DoesNotExist:
                wallet = models.OutstandingBalance.objects.create(
                    bank_acc=bank_account,
                    balance=amount,
                    updated_at=timezone.now().date()
                )
                print(wallet)

            transaction = models.OutstandingBalanceTransaction.objects.create(
                wallet=wallet,
                transaction_id=uuid.uuid4(),
                type='Credited',
                creditedAmount=amount,
                debitedAmount=None,
                status='response',
                source='bank_to_wallet',
                purpose='Funds added to wallet',
                bank_acc=bank_account,
                invoice=None,
                time_date=timezone.now()
            )
            print(transaction)

            return JsonResponse({
                "message": "Funds added successfully",
                "wallet_balance": wallet.balance,
                "transaction_id": transaction.transaction_id
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)

@csrf_exempt
def ShowFundsAPI(request,user_role_id):
    if request.method == 'GET':
        try:
            try:
                bank_acc = models.BankAccountDetails.objects.get(user_role = user_role_id)
            except models.BankAccountDetails.DoesNotExist:
                return JsonResponse({"message":"User or bank account doesn't exist"},status=404)
            balance = models.OutstandingBalance.objects.get(bank_acc= bank_acc).balance
            return JsonResponse({"Balance":balance},status = 200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET method is allowed"}, status=405)

# from_date , to_date , expiration and withdrawn
@csrf_exempt
def GetDetails(request,user_role_id):
    if request.method == 'GET':
        try:
            # InterestcutoffTime = models.AdminSettings.objects.get(id=1)
            try:
                userRole = models.UserRole.objects.get(id = user_role_id)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message":"user_role_id doesn't exist"},status=400)

            invoices = models.Invoices.objects.filter(sold=False)
            print(invoices.count())

            invoice_data_list = []
            processed_invoices = set()

            for invoice in invoices:

                fractional_units = models.FractionalUnits.objects.filter(invoice=invoice, current_owner__isnull=True)

                for unit in fractional_units:
                    post_for_sale_units = models.Post_For_Sale_UnitTracker.objects.filter(unitID=unit, sellersID__isnull=True)

                    if post_for_sale_units.exists():
                        for post_for_sale_unit in post_for_sale_units:
                            if post_for_sale_unit.post_for_saleID.user_id.user.is_admin:
                                isAdmin = True
                                break

                        invoice_data = {
                            'id' : invoice.id,
                            'Invoice_id': invoice.invoice_id,
                            'Invoice_primary_id': invoice.primary_invoice_id,
                            'Invoice_no_of_units': invoice.no_of_units,
                            'Invoice_remaining_units': invoice.no_of_units,  
                            'Invoice_per_unit_price': invoice.per_unit_price,
                            'Invoice_name': invoice.product_name,
                            'Invoice_post_date': invoice.created_At.date(),
                            'Invoice_post_time': invoice.created_At.time(),
                            'Invoice_interest': invoice.interest,
                            'Invoice_xirr': invoice.xirr,
                            'Invoice_irr': invoice.irr,
                            'Invoice_tenure_in_days': invoice.tenure_in_days,
                            'Invoice_expiration_time': invoice.expiration_time,
                            'Invoice_sold': invoice.sold,
                            # 'Interest_cut_off_time': InterestcutoffTime.interest_cut_off_time,
                            'isAdmin': isAdmin,
                            'type': 'CanBuy'
                        }
                        invoice_data_list.append(invoice_data)
                        processed_invoices.add(invoice.id)
                        break
            
            resell_invoices = models.Post_for_sale.objects.filter(
                Q(remaining_units__gt=0) & 
                ~Q(user_id=userRole)
            )

            for post_for_sale in resell_invoices:
                if not post_for_sale.user_id.user.is_admin:
                    invoice = post_for_sale.invoice_id
                    invoice_data = {
                            'id' : invoice.id,
                            'Invoice_id': invoice.invoice_id,
                            'Invoice_primary_id': invoice.primary_invoice_id,
                            'Post_for_Sell_id' : post_for_sale.id,
                            'Invoice_no_of_units': post_for_sale.no_of_units,
                            'Invoice_remaining_units': post_for_sale.no_of_units,
                            'Invoice_per_unit_price': post_for_sale.per_unit_price,
                            'Invoice_name': invoice.product_name,
                            'Invoice_post_date': post_for_sale.post_date,
                            'Invoice_post_time': post_for_sale.post_time,
                            'Invoice_interest': invoice.interest,
                            'Invoice_xirr': invoice.xirr,
                            'Invoice_irr': invoice.irr,
                            'Invoice_tenure_in_days': invoice.tenure_in_days,
                            'Invoice_expiration_time': invoice.expiration_time,
                            'Invoice_sold': invoice.sold,
                            'isAdmin': False,  
                            'type': 'CanBuy'
                        }
                    invoice_data_list.append(invoice_data)

            buyers = models.Buyers.objects.filter(user_id=userRole)
            print(buyers.count())
            for buyer in buyers:
                buyer_units = models.Buyer_UnitsTracker.objects.filter(buyer_id=buyer)
                has_posted_for_sale = buyer_units.filter(post_for_saleID__isnull=False).exists()
                
                if has_posted_for_sale:
                    # If any unit has been posted for sale, the buyer has done a post for sale
                    first_unit = buyer_units.first()
                    invoice = first_unit.unitID.invoice
                    invoice_data = {
                        'id': invoice.id,
                        'Invoice_id': invoice.invoice_id,
                        'Invoice_primary_id': invoice.primary_invoice_id,
                        'Buyer_id' : first_unit.buyer_id.id,
                        'Invoice_no_of_units': first_unit.buyer_id.no_of_units,
                        'Invoice_remaining_units': first_unit.buyer_id.no_of_units,
                        'Invoice_per_unit_price': first_unit.buyer_id.per_unit_price_invested,
                        'Invoice_name': invoice.product_name,
                        'Invoice_post_date': first_unit.buyer_id.purchase_date,
                        'Invoice_post_time': first_unit.buyer_id.purchase_time,
                        'Invoice_interest': invoice.interest,
                        'Invoice_xirr': invoice.xirr,
                        'Invoice_irr': invoice.irr,
                        'Invoice_tenure_in_days': invoice.tenure_in_days,
                        'Invoice_expiration_time': invoice.expiration_time,
                        'Invoice_sold': invoice.sold,
                        'Invoice_posted_for_sale': has_posted_for_sale,
                        'isAdmin': False,
                        'type': 'Bought'
                    }
                    invoice_data_list.append(invoice_data)
                    print(f"Buyer {buyer} has posted a unit for sale.")

                if not has_posted_for_sale:
                    # If no units have been posted for sale, the buyer has not done a post for sale
                    first_Unit = buyer_units.first()
                    invoice = first_Unit.unitID.invoice
                    invoice_data = {
                        'id': invoice.id,
                        'Invoice_id': invoice.invoice_id,
                        'Invoice_primary_id': invoice.primary_invoice_id,
                        'Buyer_id' : first_Unit.buyer_id.id,
                        'Invoice_no_of_units': first_Unit.buyer_id.no_of_units,
                        'Invoice_remaining_units': first_Unit.buyer_id.no_of_units,
                        'Invoice_per_unit_price': first_Unit.buyer_id.per_unit_price_invested,
                        'Invoice_name': invoice.product_name,
                        'Invoice_post_date': first_Unit.buyer_id.purchase_date,
                        'Invoice_post_time': first_Unit.buyer_id.purchase_time,
                        'Invoice_interest': invoice.interest,
                        'Invoice_xirr': invoice.xirr,
                        'Invoice_irr': invoice.irr,
                        'Invoice_tenure_in_days': invoice.tenure_in_days,
                        'Invoice_expiration_time': invoice.expiration_time,
                        'Invoice_sold': invoice.sold,
                        'Invoice_posted_for_sale': has_posted_for_sale,
                        'isAdmin': False,
                        'type': 'Bought'
                    }
                    invoice_data_list.append(invoice_data)
                    print(f"Buyer {buyer} has not posted any units for sale.")
            return JsonResponse({"invoices": invoice_data_list}, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET method is allowed"}, status=405)

#  funds error handling
#  invoice table no sold if fractionalunit table ma badha sold = true
@csrf_exempt
def TobuyAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            userRoleID = data.get('userRoleID')  
            invoiceID = data.get('invoiceID')  #secondary invoice id
            postForSaleID = data.get('postForSaleID')
            no_of_units = data.get('no_of_units')

            try:
                user_role = models.UserRole.objects.get(id=userRoleID)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User not found"}, status=404)

            try:
                invoice = models.Invoices.objects.get(id=invoiceID)
            except models.Invoices.DoesNotExist:
                return JsonResponse({"message": "Invoice not found"}, status=404)

            try:
                bankAcc = models.BankAccountDetails.objects.get(user_role=userRoleID)
                buyer_wallet = models.OutstandingBalance.objects.get(bank_acc=bankAcc)
            except models.OutstandingBalance.DoesNotExist:
                return JsonResponse({"message": "Buyer Wallet not found"}, status=404)
            
            try:
                postForSale = models.Post_for_sale.objects.get(id=postForSaleID)
            except models.Post_for_sale.DoesNotExist:
                return JsonResponse({"message": "postForSaleID not found"}, status=404)
            
            if postForSale.invoice_id.invoice_id != invoice.invoice_id :
                return JsonResponse({"message" : "invoiceid is not mtached"} , status=400)
            
            if postForSale.remaining_units < no_of_units:
                return JsonResponse({"message": "Not enough units available for sale"}, status=400)
            
            total_price = postForSale.per_unit_price * no_of_units

            if buyer_wallet.balance < total_price:
                return JsonResponse({"message": "Insufficient balance in buyer's wallet"}, status=400)
            
            with transaction.atomic():
                buyer = models.Buyers.objects.create(
                    user_id=user_role,
                    no_of_units=no_of_units,
                    per_unit_price_invested=postForSale.per_unit_price,
                    wallet=buyer_wallet,
                    purchase_date=timezone.now().date(),
                    purchase_time=timezone.now().time(),
                    purchase_date_time=timezone.now()
                )
                
                sales = models.Sales.objects.create(
                    UserID=postForSale.user_id,
                    Invoice=postForSale.invoice_id,
                    no_of_units=no_of_units,
                    sell_date=timezone.now().date(),
                    sell_time=timezone.now().time(),
                    sell_date_time=timezone.now()
                )
                
                units_for_sale = models.Post_For_Sale_UnitTracker.objects.filter(
                    post_for_saleID=postForSale,
                    sellersID__isnull=True
                ).order_by('id')[:no_of_units]

                if units_for_sale.count() < no_of_units:
                    return JsonResponse({"message": "Not enough units available for sale"}, status=400)

                for unit in units_for_sale:
                    unit.sellersID = sales
                    unit.save()
                    
                    models.Buyer_UnitsTracker.objects.create(
                        buyer_id=buyer,
                        unitID=unit.unitID,
                        post_for_saleID=postForSale
                    )

                    unit.unitID.sold = True
                    unit.unitID.current_owner = user_role
                    unit.unitID.save()
                
                buyer_wallet.balance -= total_price
                buyer_wallet.save()

                seller_bankAcc = models.BankAccountDetails.objects.get(user_role=postForSale.user_id)
                seller_wallet = models.OutstandingBalance.objects.get(bank_acc=seller_bankAcc)
                
                seller_wallet.balance += total_price
                seller_wallet.save()

                models.OutstandingBalanceTransaction.objects.create(
                    wallet = buyer_wallet ,
                    type = "buy" ,
                    debitedAmount = total_price ,
                    status = 'response' ,
                    source = 'wallet_to_buy',
                    bank_acc = seller_wallet.bank_acc,
                    invoice = invoice ,
                    time_date = timezone.now()
                )

                # seller
                models.OutstandingBalanceTransaction.objects.create(
                    wallet = seller_wallet ,
                    type = "sell" ,
                    creditedAmount = total_price ,
                    status = 'response' ,
                    source = 'sell_to_wallet',
                    bank_acc = buyer_wallet.bank_acc ,
                    invoice = invoice,
                    time_date = timezone.now()
                )

                postForSale.remaining_units -= no_of_units
                postForSale.save()

            return JsonResponse({"message": "Units bought successfully", "buyer_id": buyer.id}, status=201)        
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)
    
@csrf_exempt
def ToSellAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            userRoleID = data.get('userRoleID')
            buyerID = data.get('buyerID')
            invoiceID = data.get('invoiceID')
            no_of_units = data.get('no_of_units')
            per_unit_price = data.get('per_unit_price')
            from_date = data.get('from_date')
            to_date = data.get('to_date')

            if not all([userRoleID, invoiceID, no_of_units, per_unit_price]):
                return JsonResponse({"message": "All fields are required"}, status=400)

            try:
                user_role = models.UserRole.objects.get(id=userRoleID)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found"}, status=404)

            try:
                invoice = models.Invoices.objects.get(id=invoiceID)
            except models.Invoices.DoesNotExist:
                return JsonResponse({"message": "Invoice not found"}, status=404)

            try:
                buyer = models.Buyers.objects.get(id=buyerID)
            except models.Buyers.DoesNotExist:
                return JsonResponse({"message": "Buyer not found"}, status=404)

            with transaction.atomic():
                post_for_sale = models.Post_for_sale.objects.create(
                    no_of_units=no_of_units,
                    per_unit_price=per_unit_price,
                    user_id=user_role,
                    invoice_id=invoice,
                    remaining_units=no_of_units,
                    withdrawn=False,
                    post_time=timezone.now().time(),
                    post_date=timezone.now().date(),
                    from_date=from_date,
                    to_date=to_date,
                    post_dateTime=timezone.now()
                )

                units_for_selling = models.Buyer_UnitsTracker.objects.filter(
                    buyer_id=buyer
                    # post_for_saleID = None
                ).order_by('id')[:no_of_units]

                if units_for_selling.count() < no_of_units:
                    return JsonResponse({"message": "Not enough units available for selling"}, status=400)

                for unit in units_for_selling:
                    models.Post_For_Sale_UnitTracker.objects.create(
                        unitID=unit.unitID,
                        post_for_saleID=post_for_sale
                    )
                    unit.post_for_saleID = post_for_sale
                    unit.save()
                return JsonResponse({"message": "Sell transaction recorded successfully", "seller_id": user_role.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)
    
@csrf_exempt
def LedgerAPI(request, user_role_id):
    if request.method == 'GET':
        try:
            try:
                user_role = models.UserRole.objects.get(id=user_role_id)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found"}, status=404)

            bank_accounts = models.BankAccountDetails.objects.filter(user_role=user_role)
            if not bank_accounts.exists():
                return JsonResponse({"message": "No bank accounts found for this user role"}, status=404)

            wallets = models.OutstandingBalance.objects.filter(bank_acc__in=bank_accounts)
            if not wallets.exists():
                return JsonResponse({"message": "No wallets found for this user role"}, status=404)

            transactions = models.OutstandingBalanceTransaction.objects.filter(wallet__in=wallets).order_by('-time_date')

            transactions_data = []
            for transaction in transactions:
                transactions_data.append({
                    "transaction_id": str(transaction.transaction_id),
                    "type": transaction.type,
                    "creditedAmount": transaction.creditedAmount,
                    "debitedAmount": transaction.debitedAmount,
                    "status": transaction.status,
                    "source": transaction.source,
                    "purpose": transaction.purpose,
                    "bank_acc": transaction.bank_acc.account_number if transaction.bank_acc else None,
                    "invoice": transaction.invoice.name if transaction.invoice else None,
                    "time_date": transaction.time_date,
                })

            total_balance = sum(wallet.balance for wallet in wallets)

            return JsonResponse({"transactions": transactions_data, "Balance": total_balance}, status=200)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET method is allowed"}, status=405)

@csrf_exempt
def create_entry(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            time_str = data.get('interest_cut_off_time')
            
            if not time_str:
                return JsonResponse({"message": "Time is required"}, status=400)
            
            interest_cut_off_time = parse_time(time_str)
            if not interest_cut_off_time:
                return JsonResponse({"message": "Invalid time format"}, status=400)
            
            new_entry = models.AdminSettings.objects.create(interest_cut_off_time=interest_cut_off_time)
            return JsonResponse({"message": "Entry created successfully", "id": new_entry.id ,'interest_cut_of_time' : new_entry.interest_cut_off_time}, status=201)
        
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)

@csrf_exempt
def GenerateOtpAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            country_code = data.get('countryCode')
            print(country_code)
            mobile_number = data.get('mobileNumber')
            print(mobile_number)

            if not country_code or not mobile_number:
                return JsonResponse({"message": "countryCode and mobileNumber are required"}, status=400)

            url = 'https://api-preproduction.signzy.app/api/v3/phone/generateOtp'
            headers = {
                'Authorization': '0RDcUYz86vApDQQdUUxgxnjPcEbImZD4',
                'Content-Type': 'application/json'
            }

            payload = {
                "countryCode": country_code,
                "mobileNumber": mobile_number
            }

            response = requests.post(url, headers=headers, json=payload)
            print(response.json)

            if response.status_code == 200:
                return JsonResponse(response.json(), status=200)
            else:
                return JsonResponse({"message": "Failed to generate OTP"}, status=response.status_code)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)
    
@csrf_exempt
def VerifyOtpAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            country_code = data.get('countryCode')
            mobile_number = data.get('mobileNumber')
            reference_id = data.get('referenceId')
            otp = data.get('otp')
            extra_fields = data.get('extraFields')

            if not all([country_code, mobile_number, reference_id, otp, extra_fields]):
                return JsonResponse({"message": "All fields are required"}, status=400)

            url = 'https://api-preproduction.signzy.app/api/v3/phone/getNumberDetails'
            headers = {
                'Authorization': '0RDcUYz86vApDQQdUUxgxnjPcEbImZD4',
                'Content-Type': 'application/json'
            }

            payload = {
                "countryCode": country_code,
                "mobileNumber": mobile_number,
                "referenceId": reference_id,
                "otp": otp,
                "extraFields": extra_fields
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                try:
                    user = models.User.objects.get(mobile = mobile_number)
                    return JsonResponse({"message": "User registered already"}, status=400)
                except models.User.DoesNotExist:
                    user = models.User.objects.create(
                        mobile=mobile_number,
                        email="default@gmail.com"
                    )

                    return JsonResponse({
                        "message": "User registered successfully",
                        "signzy_Response" : response.json(),
                        "user_id": user.id #not register his role
                    }, status=201)
            else:
                return JsonResponse({"message": "Failed to verify OTP"}, status=response.status_code)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)
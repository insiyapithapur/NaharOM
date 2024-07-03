import uuid
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json 
from django.http import JsonResponse
from . import models
from django.utils import timezone
from django.db import transaction

@csrf_exempt
def RegisterAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mobile = data.get('mobile')
            role = data.get('role')

            if not mobile or not role:
                return JsonResponse({"message": "Mobile, password, and role are required"}, status=400)

            try:
                user = models.User.objects.get(mobile = mobile)
            except models.User.DoesNotExist:
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
            print(bank_accounts)
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
def GetDetails(request):
    if request.method == 'GET':
        # CanBuy
        invoices = models.Invoices.objects.filter(sold=False, remaining_partitions__gt=0)
        Buyer = []
        for invoice in invoices:
                invoice_data = {
                    'id': invoice.id,
                    'no_of_partitions': invoice.no_of_partitions,
                    'name': invoice.name,
                    'post_date': invoice.post_date,
                    'post_time': invoice.post_time,
                    'interest': invoice.interest,
                    'xirr': invoice.xirr,
                    'tenure_in_days' :invoice.tenure_in_days,
                    'principle_amt' : invoice.principle_amt,
                    'expiration_time' : invoice.expiration_time,
                    'remaining_partitions' : invoice.remaining_partitions,
                    'sold' : invoice.sold
                }
                Buyer.append(invoice_data)
        #CanBuy
        sellers = models.Sellers.objects.filter(sold=False, remaining_partitions__gt=0)
        invoice_list2 = []
        for seller in sellers:
            invoice = seller.Invoice
            invoice_data = {
                'id': invoice.id,
                'no_of_partitions': invoice.no_of_partitions,
                'name': invoice.name,
                'Admin post_date': invoice.post_date,
                ' Admin post_time': invoice.post_time,
                'interest': invoice.interest,
                'xirr': invoice.xirr,
                'tenure_in_days' :invoice.tenure_in_days,
                'Admin principle_amt' : invoice.principle_amt,
                'expiration_time' : invoice.expiration_time,
                'User' : seller.User,
                'amount' : seller.amount,
                'sell_date' :seller.sell_date,
                'sell_time' : seller.sell_time,
                'remaining_partitions' :seller.remaining_partitions,
                'sold' : seller.sold
            }
            Buyer.append(invoice_data)

        return JsonResponse({"Buyer": Buyer}, status=200)
    else:
        return JsonResponse({"message": "Only GET methods are allowed"}, status=405)
    
# After each successfully creation of rows in all tables it should send success msg to frontEnd
# fractional_unit_ID will be in array
# check the fractional_unit_IDs user is requesting is with whom if fractional_unit_ID is
# her/his only then send msg
# @csrf_exempt
# def TobuyAPI(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             user_role_id = data.get('user_role_id')
#             invoice_secondary_id = data.get('invoice_secondary_id')
#             wallet_id = data.get('wallet_id')
#             seller_id = data.get('seller_id')
#             fractional_unit_id = data.get('fractional_unit_id')

#             try:
#                 user_role = models.UserRole.objects.get(id=user_role_id)
#             except models.UserRole.DoesNotExist:
#                 return JsonResponse({"message": "User role not found"}, status=404)

#             try:
#                 invoice = models.Invoices.objects.get(id=invoice_secondary_id)
#             except models.Invoices.DoesNotExist:
#                 return JsonResponse({"message": "Invoice not found"}, status=404)

#             try:
#                 wallet = models.OutstandingBalance.objects.get(id=wallet_id)
#             except models.OutstandingBalance.DoesNotExist:
#                 return JsonResponse({"message": "Wallet not found"}, status=404)

#             no_of_partition = data.get('no_of_partition')
#             total_amount_invested = data.get('total_amount_invested')
#             purchase_date = timezone.now().date()
#             purchase_time = timezone.now().time()

#             if not all([no_of_partition, total_amount_invested]):
#                 return JsonResponse({"message": "All fields are required"}, status=400)

#             if wallet.balance < total_amount_invested:
#                 return JsonResponse({"message": "Insufficient funds in the wallet"}, status=400)

#             with transaction.atomic():
#                 buyer = models.Buyers.objects.create(
#                     user=user_role,
#                     invoice=invoice,
#                     no_of_partitions=no_of_partition,
#                     total_amount_invested=total_amount_invested,
#                     wallet=wallet,
#                     purchase_date=purchase_date,
#                     purchase_time=purchase_time,
#                 )

#                 if seller_id:
#                     try:
#                         seller = models.Sellers.objects.get(id=seller_id)
#                         print(seller.remaining_partitions)
#                     except models.Sellers.DoesNotExist:
#                         return JsonResponse({"message": "Seller not found or not enough partitions available"}, status=404)

#                     seller_wallet = seller.wallet

#                     if fractional_unit_id:
#                         try:
#                             # this is checking if fractional_unit_id is already exist or not 
#                             fractional_unit = models.FractionalUnits.objects.get(unit_id=fractional_unit_id, invoice=invoice, current_owner=seller.buyer.user, sold=True)
#                             fractional_units = [fractional_unit]
#                         except models.FractionalUnits.DoesNotExist:
#                             return JsonResponse({"message": "Requested fractional unit not available"}, status=404)
#                     else:
#                         fractional_units = models.FractionalUnits.objects.filter(invoice=invoice ,  sold=False)[:no_of_partition]
#                         if len(fractional_units) < no_of_partition:
#                             return JsonResponse({"message": "Not enough fractional units available"}, status=400)

#                     for unit in fractional_units:
#                         unit.sold = True
#                         unit.current_owner = user_role
#                         unit.save()

#                         models.SalePurchaseReport.objects.create(
#                             unit=unit,
#                             seller=seller,
#                             buyer=buyer,
#                         )

#                     seller.remaining_partitions -= no_of_partition
#                     if seller.remaining_partitions == 0:
#                         seller.someone_purchased = True
#                     seller.save()

#                     seller_wallet.balance += total_amount_invested
#                     seller_wallet.save()

#                     models.OutstandingBalanceTransaction.objects.create(
#                         wallet=seller_wallet,
#                         transaction_id=uuid.uuid4(),
#                         type='sell',
#                         creditedAmount=total_amount_invested,
#                         debitedAmount=0,
#                         status='response',
#                         source='wallet_to_sell',
#                         purpose='Funds received from selling',
#                         bank_acc=None,
#                         invoice=invoice,
#                         time_date=timezone.now()
#                     )

#                 else:
#                     fractional_units = models.FractionalUnits.objects.filter(invoice=invoice, sold=False)[:no_of_partition]
#                     for unit in fractional_units:
#                         unit.sold = True
#                         unit.current_owner = user_role
#                         unit.save()

#                 if wallet.balance < total_amount_invested:
#                     return JsonResponse({"message": "Insufficient funds in the wallet"}, status=400)
#                 else:
#                     wallet.balance -= total_amount_invested
#                     wallet.save()

#                 models.OutstandingBalanceTransaction.objects.create(
#                     wallet=wallet,
#                     transaction_id=uuid.uuid4(),
#                     type='buy',
#                     creditedAmount=0,
#                     debitedAmount=total_amount_invested,
#                     status='response',
#                     source='wallet_to_buy',
#                     purpose='Funds used for purchasing',
#                     bank_acc=None,
#                     invoice=invoice,
#                     time_date=timezone.now()
#                 )

#             return JsonResponse({"message": "Transaction completed successfully", "buyer_id": buyer.id}, status=201)

#         except json.JSONDecodeError:
#             return JsonResponse({"message": "Invalid JSON"}, status=400)
#         except Exception as e:
#             return JsonResponse({"message": str(e)}, status=500)

#     else:
#         return JsonResponse({"message": "Only POST method is allowed"}, status=405)
@csrf_exempt
def TobuyAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_role_id = data.get('user_role_id')  
            invoice_secondary_id = data.get('invoice_secondary_id')
            wallet_id = data.get('wallet_id')
            seller_id = data.get('seller_id') #if 2nd buyer
            no_of_partition = data.get('no_of_partition')
            total_amount_invested = data.get('total_amount_invested')
            purchase_date = timezone.now().date()
            purchase_time = timezone.now().time()

            try:
                user_role = models.UserRole.objects.get(id=user_role_id)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found"}, status=404)

            try:
                invoice = models.Invoices.objects.get(id=invoice_secondary_id)
            except models.Invoices.DoesNotExist:
                return JsonResponse({"message": "Invoice not found"}, status=404)

            try:
                buyer_wallet = models.OutstandingBalance.objects.get(id=wallet_id)
            except models.OutstandingBalance.DoesNotExist:
                return JsonResponse({"message": "Buyer Wallet not found"}, status=404)

            if not all([no_of_partition, total_amount_invested]):
                return JsonResponse({"message": "All fields are required"}, status=400)

            with transaction.atomic():
                if seller_id:
                    try:
                        seller = models.Sellers.objects.get(id=seller_id)
                    except models.Sellers.DoesNotExist:
                        return JsonResponse({"message": "Seller not found"}, status=404)
                    
                    if seller.remaining_partitions < no_of_partition :
                        return JsonResponse({"message": "Not enough fractional units available"}, status=400)
                    
                    fractional_units = models.FractionalUnits.objects.filter(
                        current_owner=seller.User, sold=True)[:no_of_partition]
                    fractional_units_count = fractional_units.count()
                    # print("fractional_units_count ",fractional_units_count)

                    if fractional_units_count < no_of_partition :
                        return JsonResponse({"message": "Not enough fractional units available"}, status=400)
                    
                    buyer = models.Buyers.objects.create(
                        user=user_role,
                        invoice=invoice,
                        no_of_partitions=no_of_partition,
                        total_amount_invested=total_amount_invested,
                        wallet=buyer_wallet,
                        purchase_date=purchase_date,
                        purchase_time=purchase_time,
                    )
                    
                    for unit in fractional_units:
                        unit.current_owner = user_role
                        unit.save()
                        models.SalePurchaseReport.objects.create(
                            unit=unit,
                            seller=seller,
                            buyer=buyer,
                            transaction_date=timezone.now()
                        )

                    seller.remaining_partitions -= no_of_partition
                    if seller.remaining_partitions == 0:
                        seller.sold = True
                    seller.save()
                    # print("seller.remaining_partitions after buying ",seller.remaining_partitions)

                    seller_wallet = seller.wallet
                    # print("seller_wallet.balance " ,seller_wallet.balance)
                    seller_wallet.balance += total_amount_invested
                    seller_wallet.save()

                    models.OutstandingBalanceTransaction.objects.create(
                        wallet=seller_wallet,
                        transaction_id=uuid.uuid4(),
                        type='sell',
                        creditedAmount=total_amount_invested,
                        debitedAmount=0,
                        status='response',
                        source='wallet_to_sell',
                        purpose='Funds received from selling',
                        bank_acc=None,
                        invoice=invoice,
                        time_date=timezone.now()
                    )

                    if buyer_wallet.balance < total_amount_invested:
                        return JsonResponse({"message": "Insufficient funds in the wallet"}, status=400)
                    else:
                        buyer_wallet.balance -= total_amount_invested
                        buyer_wallet.save()

                    models.OutstandingBalanceTransaction.objects.create(
                        wallet=buyer_wallet,
                        transaction_id=uuid.uuid4(),
                        type='buy',
                        creditedAmount=0,
                        debitedAmount=total_amount_invested,
                        status='response',
                        source='wallet_to_buy',
                        purpose='Funds used for purchasing',
                        bank_acc=None,
                        invoice=invoice,
                        time_date=timezone.now()
                    )

                    return JsonResponse({"message": "Transaction completed successfully", "buyer_id": buyer.id}, status=201)
                else:
                    fractional_units = models.FractionalUnits.objects.filter(
                        current_owner=None, sold=False)[:no_of_partition]
                    fractional_units_count = fractional_units.count()
                    # print("fractional_units_count ",fractional_units_count)

                    if fractional_units_count < no_of_partition :
                        return JsonResponse({"message": "Not enough fractional units available"}, status=400)
                    
                    buyer = models.Buyers.objects.create(
                        user=user_role,
                        invoice=invoice,
                        no_of_partitions=no_of_partition,
                        total_amount_invested=total_amount_invested,
                        wallet=buyer_wallet,
                        purchase_date=purchase_date,
                        purchase_time=purchase_time,
                    )

                    for unit in fractional_units:
                        unit.current_owner = user_role
                        unit.sold = True
                        unit.save()
                    
                    if buyer_wallet.balance < total_amount_invested:
                        return JsonResponse({"message": "Insufficient funds in the wallet"}, status=400)
                    else:
                        buyer_wallet.balance -= total_amount_invested
                        buyer_wallet.save()

                    models.OutstandingBalanceTransaction.objects.create(
                        wallet=buyer_wallet,
                        transaction_id=uuid.uuid4(),
                        type='buy',
                        creditedAmount=0,
                        debitedAmount=total_amount_invested,
                        status='response',
                        source='wallet_to_buy',
                        purpose='Funds used for purchasing',
                        bank_acc=None,
                        invoice=invoice,
                        time_date=timezone.now()
                    )
                    Remaining_fraction  = models.FractionalUnits.objects.filter(
                        sold=False , invoice = invoice)
                    
                    Remaining_fraction_count = Remaining_fraction.count()
                    print("Remaining_fraction_count ",Remaining_fraction_count)

                    if Remaining_fraction_count:
                        invoice.remaining_partitions = Remaining_fraction_count
                        invoice.save()
                    else:
                        invoice.remaining_partitions = 0
                        invoice.sold = True
                        invoice.save()
                    return JsonResponse({"message": "Transaction completed successfully", "buyer_id": buyer.id}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)
    
# after making first post to sell add remaining_partition if it is not first post to sell
# for that invoice then check remaining_partition
@csrf_exempt
def ToSellAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_role_id = data.get('user_role_id')
            invoice_id = data.get('invoice_id')
            no_of_fractions = data.get('no_fractions')
            amount = data.get('amount')

            if not all([user_role_id, invoice_id, no_of_fractions, amount]):
                return JsonResponse({"message": "All fields are required"}, status=400)
            
            try:
                user_role = models.UserRole.objects.get(id=user_role_id)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found"}, status=404)
            # print("user_role ",user_role)

            with transaction.atomic():
                Had_no_of_fraction = models.FractionalUnits.objects.filter(invoice = invoice_id , current_owner = user_role_id).count()
                # print("Had_no_of_fraction " , Had_no_of_fraction)

                if not Had_no_of_fraction:
                    return JsonResponse({"message": "No fractions for sell"}, status=404)
                
                if Had_no_of_fraction < no_of_fractions:
                    return JsonResponse({"message": "Not enough partitions to sell"}, status=400)

                try:
                    bankAcc = models.BankAccountDetails.objects.get(user_role=user_role)
                except models.BankAccountDetails.DoesNotExist:
                    return JsonResponse({"message": "BankAcc not found"}, status=404)
               
                try:
                    wallet = models.OutstandingBalance.objects.get(bank_acc=bankAcc)
                except models.OutstandingBalance.DoesNotExist:
                    return JsonResponse({"message": "Wallet not found"}, status=404)
            
                sell_date = timezone.now().date()
                sell_time = timezone.now().time()
            
                seller = models.Sellers.objects.create(
                    User=user_role,
                    amount=amount,
                    wallet=wallet,
                    no_of_partitions=no_of_fractions,
                    sell_date=sell_date,
                    sell_time=sell_time,
                    remaining_partitions=no_of_fractions,
                    sold=False
                )
                # print(seller)
                return JsonResponse({"message": "Sell transaction recorded successfully", "seller_id": seller.id}, status=201)

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

            return JsonResponse({"transactions": transactions_data}, status=200)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET method is allowed"}, status=405) 

@csrf_exempt
def BuyerIRRAPI(request,user_role_id):
    if request.method == 'GET':
        try:
            try:
                user_role = models.UserRole.objects.get(id=user_role_id)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found"}, status=404)
            
            # here all this field will be come from primary platform
            # Interest Actual = (IRR * fractional_Unit_Value * tenure) / 365
            # Total Earnings = Interest Actual + Expected Profit 
            response_data = {
                "XIRR": "18%",
                "No of Days": 30,
                "Interest Actual": 8219.178082,
                # "Total Earnings": 13219.17808
            }

            return JsonResponse(response_data, status=200)
        except Exception as e:
            return JsonResponse({"message": "An error occurred: " + str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET method is allowed"}, status=405)
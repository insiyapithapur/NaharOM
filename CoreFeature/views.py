import json
from random import randint
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.utils import timezone
from SecondaryTradingPlatform import settings
from . import models
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login

@csrf_exempt
def LoginAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            role = data.get('role')

            if not email or not password or not role:
                return JsonResponse({"message": "Email, password, and role are required"}, status=400)

            try:
                user = models.User.objects.get(email=email)
                # print(user)
                if user.check_password(password):
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
# def RegisterAPI(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             email = data.get('email')
#             password = data.get('password')
#             role = data.get('role')

#             if not email or not password or not role:
#                 return JsonResponse({"message": "Email, password, and role are required"}, status=400)

#             if models.UserRole.objects.filter(user__email=email, role=role).exists():
#                 return JsonResponse({"message": "Email already exists with this role"}, status=400)

#             user = models.User.objects.create(
#                 email=email,
#                 password=make_password(password)
#             )

#             user_role = models.UserRole.objects.create(
#                 user=user,
#                 role=role
#             )

#             return JsonResponse({"message": "Registration successful", "user_role_id": user_role.id}, status=201)

#         except json.JSONDecodeError:
#             return JsonResponse({"message": "Invalid JSON"}, status=400)
#         except Exception as e:
#             return JsonResponse({"message": str(e)}, status=500)
#     else:
#         return JsonResponse({"message": "Only POST method is allowed"}, status=405)

@csrf_exempt
def RegisterAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            role = data.get('role')

            if not email or not password or not role:
                return JsonResponse({"message": "Email, password, and role are required"}, status=400)

            try:
                user = models.User.objects.get(email=email)
            except models.User.DoesNotExist:
                user = models.User.objects.create(
                    email=email,
                    password=make_password(password)
                )
                user_role = models.UserRole.objects.create(
                    user=user,
                    role=role,
                    registration=True
                )

                return JsonResponse({
                    "message": "Role added to existing user",
                    "user_role_id": user_role.id
                }, status=201)
            
            existing_roles = models.UserRole.objects.filter(user=user).values_list('role', flat=True)
            if role in existing_roles:
                return JsonResponse({"message": f"User already registered with role '{role}'"}, status=400)
            
            if 'company' in existing_roles and 'individual' in existing_roles:
                return JsonResponse({"message": "Already created both roles for this email"}, status=400)

            user_role = models.UserRole.objects.create(
                user=user,
                role=role
            )
            return JsonResponse({"message": "Role added to existing user", "user_role_id": user_role.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)
    
@csrf_exempt
def LoginAsIndividualAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_role_id = data.get('user_role_id')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            city = data.get('city')
            state = data.get('state')
            pin_code = data.get('pin_code')
            phone_no = data.get('phone_no')
            security_question_id = data.get('security_question_id')
            security_question_ans = data.get('security_question_ans')

            if not user_role_id or not first_name or not last_name or not city or not state or not pin_code or not phone_no or not security_question_id or not security_question_ans:
                return JsonResponse({"message": "All fields are required"}, status=400)

            try:
                user_role = models.UserRole.objects.get(id=user_role_id)
                if user_role.role != 'individual':
                    return JsonResponse({"message": "UserRole does not match 'individual' role"}, status=400)

                security_question = models.SecurityQuestion.objects.get(id=security_question_id)
                user_role.user_profile = True
                user_role.save()

                individual_details = models.IndividualDetails.objects.create(
                    user_role=user_role,
                    first_name=first_name,
                    last_name=last_name,
                    city=city,
                    state=state,
                    pin_code=pin_code,
                    phone_no=phone_no,
                    security_question=security_question,
                    security_question_ans=security_question_ans
                )

                return JsonResponse({"message": "Login as individual successful", "individual_id": individual_details.id , 'user_role_id' : user_role.id}, status=201)

            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "UserRole ID does not exist"}, status=404)
            except models.SecurityQuestion.DoesNotExist:
                return JsonResponse({"message": "SecurityQuestion ID does not exist"}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)

@csrf_exempt
def LoginAsCompanyAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_role_id = data.get('user_role_id')

            if not user_role_id:
                return JsonResponse({"message": "user_role_id is required"}, status=400)
            
            try:
                user_role = models.UserRole.objects.get(id=user_role_id, role='company')
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found or is not a company role"}, status=404)
            
            try:
                company_details = models.CompanyDetails.objects.get(user_role=user_role)
                return JsonResponse({"message": f"Company details already exist for user_role_id {user_role_id}"}, status=400)
            except models.CompanyDetails.DoesNotExist:
                pass

            user_role.user_profile = True
            user_role.save()
            
            try:
                company_name = data.get('company_name')
                company_address = data.get('company_address')
                city = data.get('city')
                state = data.get('state')
                pin_no = data.get('pin_no')
                phone_no = data.get('phone_no')
                company_pan_no = data.get('company_pan_no')
                public_url_company = data.get('public_url_company')
                security_question_id = data.get('security_question_id')
                security_question_ans = data.get('security_question_ans')

                if security_question_id:
                    try:
                        models.SecurityQuestion.objects.get(id=security_question_id)
                    except models.SecurityQuestion.DoesNotExist:
                        return JsonResponse({"message": "Security question not found"}, status=404)

                company_details, created = models.CompanyDetails.objects.get_or_create(
                    user_role=user_role,
                    defaults={
                        'company_name': company_name,
                        'company_address': company_address,
                        'city': city,
                        'state': state,
                        'pin_no': pin_no,
                        'phone_no': phone_no,
                        'company_pan_no': company_pan_no,
                        'public_url_company': public_url_company,
                        'security_question_id': security_question_id,
                        'security_question_ans': security_question_ans,
                    }
                )

                if not created:
                    company_details.company_name = company_name
                    company_details.company_address = company_address
                    company_details.city = city
                    company_details.state = state
                    company_details.pin_no = pin_no
                    company_details.phone_no = phone_no
                    company_details.company_pan_no = company_pan_no
                    company_details.public_url_company = public_url_company
                    company_details.security_question_id = security_question_id
                    company_details.security_question_ans = security_question_ans
                    company_details.save()

                return JsonResponse({"message": "Company details saved successfully" , "company_details_id": company_details.id , 'user_role_id' : user_role.id}, status=200)

            except KeyError:
                return JsonResponse({"message": "Missing required fields"}, status=400)

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

                user_role.CheckBankAccountDetails = True
                user_role.save()

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
def PanCardDetailsAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_role_id = data.get('user_role_id')
            pan_card_no = data.get('pan_card_no')

            if not user_role_id or not pan_card_no:
                return JsonResponse({"message": "user_role_id and pan_card_no are required"}, status=400)

            try:
                user_role = models.UserRole.objects.get(id=user_role_id)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found"}, status=404)

            if models.PanCardNos.objects.filter(user_role=user_role).exists():
                return JsonResponse({"message": "PAN card number already exists for this user role"}, status=400)

            pan_card_details = models.PanCardNos.objects.create(
                user_role=user_role,
                pan_card_no=pan_card_no
            )

            user_role.CheckPanCardNo = True
            user_role.save()

            return JsonResponse({"message": "PAN card details saved successfully", "pan_card_id": pan_card_details.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)

# @csrf_exempt
# def GenerateOTPAPI(request, user_role_id):
#     if request.method == 'GET':
#         try:
#             try:
#                 user_role = models.UserRole.objects.get(id=user_role_id)
#             except models.UserRole.DoesNotExist:
#                 return JsonResponse({"message": "User role not found"}, status=404)

#             user_email = user_role.user.email

#             random_code = randint(100000, 999999)
#             subject = 'OTP from Secondary Trading platform'
#             message = f'Your OTP is {random_code}'
#             email_from = settings.EMAIL_HOST_USER
#             recipient_list = [user_email]
#             send_mail(subject, message, email_from, recipient_list)

#             return JsonResponse({"message": "OTP sent successfully"}, status=200)

#         except Exception as e:
#             return JsonResponse({"message": str(e)}, status=500)

#     else:
#         return JsonResponse({"message": "Only GET method is allowed"}, status=405)

@csrf_exempt
def AddFundsAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_role_id = data.get('user_role_id')
            bank_acc_id = data.get('bank_acc_id')
            amount = data.get('amount')

            if not user_role_id or not bank_acc_id or not amount:
                return JsonResponse({"message": "user_role_id, bank_acc_id, and amount are required"}, status=400)

            try:
                user_role = models.UserRole.objects.get(id=user_role_id)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found"}, status=404)

            try:
                bank_account = models.BankAccountDetails.objects.get(id=bank_acc_id, user_role=user_role)
            except models.BankAccountDetails.DoesNotExist:
                return JsonResponse({"message": "Bank account not found for the given user role"}, status=404)

            try:
                wallet = models.Wallet.objects.get(bank_acc=bank_account)
                wallet.balance += amount
                wallet.save()
            except models.Wallet.DoesNotExist:
                wallet = models.Wallet.objects.create(
                    bank_acc=bank_account,
                    balance=amount
                )

            transaction = models.WalletTransaction.objects.create(
                wallet=wallet,
                credited=True,
                debited=False,
                bank_acc=bank_account,
                amount = amount,
                status='response'
            )

            user_role.CheckFunds = True
            user_role.save()

            return JsonResponse({
                "message": "Funds added successfully",
                "wallet_balance": wallet.balance,
                "transaction_id": transaction.id
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)

@csrf_exempt
def CheckBooleansAPI(request, user_role_id):
    if request.method == "GET":
        try:
            user_role = models.UserRole.objects.get(id=user_role_id)
            
            warnings = {
                "Complete the user profile": None,
                "Bank account": None,
                "PAN No.": None,
                "Add Funds": None
            }
            
            if not user_role.user_profile:
                warnings["Bank account"] = "This should not be enabled"
                warnings["PAN No."] = "This should not be enabled"
                warnings["Add Funds"] = "This should not be enabled"
            elif not user_role.CheckBankAccountDetails:
                warnings["Add Funds"] = "This should not be enabled"
            
            return JsonResponse({
                "completionBooleans": [
                    {
                        "label": "Complete the registration",
                        "value": user_role.registration,
                        "warning": None
                    },
                    {
                        "label": "Complete the user profile",
                        "value": user_role.user_profile,
                        "warning": warnings["Complete the user profile"]
                    },
                    {
                        "label": "Bank account",
                        "value": user_role.CheckBankAccountDetails,
                        "warning": warnings["Bank account"]
                    },
                    {
                        "label": "PAN No.",
                        "value": user_role.CheckPanCardNo,
                        "warning": warnings["PAN No."]
                    },
                    {
                        "label": "Add Funds",
                        "value": user_role.CheckFunds,
                        "warning": warnings["Add Funds"]
                    }
                ]
            }, status=200)
        except models.UserRole.DoesNotExist:
            return JsonResponse({"message": "User role not found"}, status=404)

    else:
        return JsonResponse({"message": "Only GET method is allowed"}, status=405)

@csrf_exempt
def AdminLoginAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({"message": "Email and password are required"}, status=400)

            user = authenticate(request, email=email, password=password)

            if user is None:
                return JsonResponse({"message": "Invalid credentials"}, status=401)

            if not user.is_admin:
                return JsonResponse({"message": "You do not have admin privileges"}, status=403)

            login(request, user)

            return JsonResponse({"message": "Admin logged in successfully"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)

@csrf_exempt
def InvoicesAPI(request):
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

            if not user_role.user.is_admin:
                return JsonResponse({"message": "For this operation you have to register yourself with admin role"}, status=403)
            
            primary_invoice_id = data.get('primary_invoice_id')
            no_of_fractional_Unit = data.get('no_of_fractional_Unit')
            Discounting = data.get('Discounting')
            company_description = data.get('company_description')
            networth_of_company = data.get('networth_of_company')
            name = data.get('name')
            InvoiceTotalPrice = data.get('InvoiceTotalPrice')
            post_date = timezone.now().date()
            post_time = timezone.now().time()

            if not all([primary_invoice_id, no_of_fractional_Unit, Discounting, company_description, networth_of_company, name , InvoiceTotalPrice]):
                return JsonResponse({"message": "All fields are required"}, status=400)

            invoice = models.Invoices.objects.create(
                primary_invoice_id=primary_invoice_id,
                no_of_fractional_Unit=no_of_fractional_Unit,
                Discounting=Discounting,
                company_description=company_description,
                networth_of_company=networth_of_company,
                name=name , 
                InvoiceTotalPrice = InvoiceTotalPrice , 
                PostDate = post_date ,
                PostTime = post_time 
            )

            return JsonResponse({"message": "Invoice created successfully", "invoice_id": invoice.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

    elif request.method == 'GET':
        invoices = models.Invoices.objects.all().values(
            'id', 'primary_invoice_id', 'no_of_fractional_Unit', 'Discounting', 'company_description', 'networth_of_company', 'name' ,'InvoiceTotalPrice' , 'PostDate' , 'PostTime'
        )
        return JsonResponse(list(invoices), safe=False, status=200)

    else:
        return JsonResponse({"message": "Only POST and GET methods are allowed"}, status=405)
        
@csrf_exempt
def TobuyAPI(request, invoice_secondary_id, user_role_id, wallet_id):
    if request.method == 'POST':
        try:
            
            try:
                user_role = models.UserRole.objects.get(id=user_role_id)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found"}, status=404)

            try:
                invoice = models.Invoices.objects.get(id=invoice_secondary_id)
            except models.Invoices.DoesNotExist:
                return JsonResponse({"message": "Invoice not found"}, status=404)

            try:
                wallet = models.Wallet.objects.get(id=wallet_id)
            except models.Wallet.DoesNotExist:
                return JsonResponse({"message": "Wallet not found"}, status=404)

            data = json.loads(request.body)
            no_of_partition = data.get('no_of_partition')
            total_amount_invested = data.get('total_amount_invested')
            purchaseDate = data.get('purchaseDate')  # YYYY-MM-DD format
            purchaseTime = data.get('purchaseTime')  #  HH:MM format

            if not all([no_of_partition, total_amount_invested, purchaseDate, purchaseTime]):
                return JsonResponse({"message": "All fields are required"}, status=400)

            buyer = models.Buyer.objects.create(
                invoice=invoice,
                user=user_role,
                no_of_partition=no_of_partition,
                total_amount_invested=total_amount_invested,
                wallet=wallet,
                purchaseDate=purchaseDate,
                purchaseTime=purchaseTime,
            )

            invoice.SomeonePurchase = True
            invoice.save()

            if wallet.balance >= total_amount_invested:
                wallet.balance -= total_amount_invested
                wallet.save()
            else:
                return JsonResponse({"message": "Insufficient funds in the wallet"}, status=400)

            transaction = models.WalletTransaction.objects.create(
                wallet=wallet,
                credited=False,
                debited=True,
                status='response',
                transaction_type='wallet_to_buy',
                invoice=invoice
            )

            return JsonResponse({"message": "Transaction completed successfully", "buyer_id": buyer.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)

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



@csrf_exempt
def SecurityQuestionAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question')

            if not question:
                return JsonResponse({"message": "Question is required"}, status=400)

            if models.SecurityQuestion.objects.filter(question=question).exists():
                return JsonResponse({"message": "Security question exists"}, status=400)

            models.SecurityQuestion.objects.create(question=question)
            return JsonResponse({"message": "OK"}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    
    elif request.method == 'GET':
        try:
            security_questions = models.SecurityQuestion.objects.all()
            questions_list = []
            for question in security_questions:
                questions_list.append({
                    "id": question.id,
                    "question": question.question
                })
            return JsonResponse(questions_list, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET and POST methods are allowed"}, status=405)
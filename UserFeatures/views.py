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

# @csrf_exempt
# def RegisterAPI(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             mobile = data.get('mobile')
#             role = data.get('role')

#             if not mobile or not role:
#                 return JsonResponse({"message": "Mobile and role are required"}, status=400)

#             try:
#                 user = models.User.objects.get(mobile = mobile)
#                 user_role = models.UserRole.objects.get(user = user , role = role)
#                 return JsonResponse({"message": "User already exist"}, status=400)
#             except models.UserRole.DoesNotExist:
#                 #  api integrate , mobile --> email
#                 user = models.User.objects.create(
#                     mobile=mobile,
#                     email="default8141@gmail.com"
#                 )
#                 user_role = models.UserRole.objects.create(
#                     user=user,
#                     role=role
#                 )

#                 return JsonResponse({
#                     "message": "User registered successfully",
#                     "user_role_id": user_role.id
#                 }, status=201)
            
#             # existing_roles = models.UserRole.objects.filter(user=user).values_list('role', flat=True)
#             # if role in existing_roles:
#             #     return JsonResponse({"message": f"User already registered with role '{role}'"}, status=400)
            
#             # if 'company' in existing_roles and 'individual' in existing_roles:
#             #     return JsonResponse({"message": "Already created both roles for this email"}, status=400)

#             # user_role = models.UserRole.objects.create(
#             #     user=user,
#             #     role=role
#             # )
#             # return JsonResponse({"message": "Role added to existing user", "user_role_id": user_role.id}, status=201)

#         except json.JSONDecodeError:
#             return JsonResponse({"message": "Invalid JSON"}, status=400)
#         except Exception as e:
#             return JsonResponse({"message": str(e)}, status=500)
#     else:
#         return JsonResponse({"message": "Only POST method is allowed"}, status=405)
    
# @csrf_exempt
# def LoginAPI(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             mobile = data.get('mobile')
#             role = data.get('role')

#             if not mobile or not role:
#                 return JsonResponse({"message": "Email, password, and role are required"}, status=400)

#             try:
#                 user = models.User.objects.get(mobile=mobile)
#                 print(user)
#                 if user:
#                     try:
#                         user_role = models.UserRole.objects.get(user=user, role=role)
#                         return JsonResponse({"message": "Login successful", "user_role_id": user_role.id}, status=200)
#                     except models.UserRole.DoesNotExist:
#                         return JsonResponse({"message": "Role mismatch for the given email"}, status=400)
#                 else:
#                     return JsonResponse({"message": "Invalid email or password"}, status=401)
#             except models.User.DoesNotExist:
#                 return JsonResponse({"message": "Email doesn't exist"}, status=401)
#         except json.JSONDecodeError:
#             return JsonResponse({"message": "Invalid JSON"}, status=400)
#     else:
#         return JsonResponse({"message": "Only POST method is allowed"}, status=405)

# @csrf_exempt
# def ChangeStatusAPI(request):
#     if request.method == 'GET':

@csrf_exempt
def GenerateOtpAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            country_code = data.get('countryCode')
            mobile_number = data.get('mobileNumber')

            if not country_code or not mobile_number:
                return JsonResponse({"message": "countryCode and mobileNumber are required"}, status=400)

            url = 'https://api-preproduction.signzy.app/api/v3/phone/generateOtp'
            headers = {
                'Authorization': '34a0GzKikdWkAHuTY2rQsOvDZIZgrODz',
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
                return JsonResponse({"message": response.json()}, status=response.status_code)
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
            user_role = data.get('user_role')

            if not all([country_code, mobile_number, user_role ,reference_id, otp, str(extra_fields)]):
                return JsonResponse({"message": "All fields are required"}, status=400)

            url = 'https://api-preproduction.signzy.app/api/v3/phone/getNumberDetails'
            headers = {
                'Authorization': '34a0GzKikdWkAHuTY2rQsOvDZIZgrODz',
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
            print("response")

            if response.status_code == 200:
                try:
                    user = models.User.objects.get(mobile = mobile_number)
                    userRole = models.UserRole.objects.get(user = user)
                    if userRole.role != user_role:
                        return JsonResponse({"message":"user role is not match"},status=400)
                    return JsonResponse({
                            "message": "User already registered",
                            "signzy_Response" : response.json(),
                            "user_id": userRole.id 
                        }, status=200)
                except models.User.DoesNotExist:
                    with transaction.atomic():
                        user = models.User.objects.create(
                            mobile=mobile_number,
                            email="default@gmail.com"
                        )
                        userRole = models.UserRole.objects.create(
                            user = user,
                            role = user_role,
                        )
                        return JsonResponse({
                            "message": "User registered successfully",
                            "signzy_Response" : response.json(),
                            "user": userRole.id 
                        }, status=201)
                except models.UserRole.DoesNotExist:
                    return JsonResponse({"message":"User id exist but not userRole"},status=404)
            else:
                return JsonResponse({"message": response.json()}, status=response.status_code)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)

@csrf_exempt
def verifyStatusAPI(request,user):
    if request.method == 'GET':
        try:
            if not user:
                return JsonResponse({"message": "userID should be there in url"}, status=400)

            userRole = models.UserRole.objects.get(id=user)

            if userRole.role == 'Individual' :
                Individual_Detials_exist = models.IndividualDetails.objects.filter(user_role=userRole).exists()
                BankAcc_Details_exist = models.BankAccountDetails.objects.filter(user_role=userRole).exists()
                if Individual_Detials_exist :
                    is_KYC = True
                else :
                    is_KYC = False
                if BankAcc_Details_exist :
                    is_BankDetailsExists = True
                else :
                    is_BankDetailsExists = False

            elif userRole.role == 'Company' :
                Company_Detials_exist = models.CompanyDetails.objects.filter(user_role=userRole).exists()
                BankAcc_Details_exist = models.BankAccountDetails.objects.filter(user_role=userRole).exists()
                if Company_Detials_exist :
                    is_KYC = True
                else :
                    is_KYC = False
                if BankAcc_Details_exist :
                    is_BankDetailsExists = True
                else :
                    is_BankDetailsExists = False

            return JsonResponse({"is_KYC": is_KYC , "is_BankDetailsExists":is_BankDetailsExists,"user": userRole.id  , 'user_role' : userRole.role , 'phone' : userRole.user.mobile ,"is_admin" : str(userRole.user.is_admin) , "is_superAdmin" : str(userRole.user.is_superadmin) },status=200)
        
        except models.UserRole.DoesNotExist:
            return JsonResponse({"message" : "user ID does not exist"},status=400) 
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET methods are allowed"}, status=405)

@csrf_exempt
def phonetoPrefillAPI(request,user):
    if request.method == 'GET':
        try:
            if not all([user]):
                return JsonResponse({"message": "user is required"}, status=400)
      
            userRole = models.UserRole.objects.get(id=user)

            url = 'https://api-preproduction.signzy.app/api/v3/phonekyc/phone-prefill-v2'
            headers = {
                'Authorization': '34a0GzKikdWkAHuTY2rQsOvDZIZgrODz',
                'Content-Type': 'application/json'
            }

            payload = {
                "mobileNumber": userRole.user.mobile,
                "consent": {
                    "consentFlag": True,
                    "consentTimestamp": 17000,
                    "consentIpAddress": "684D:1111:222:3333:4444:5555:6:77",
                    "consentMessageId": "CM_1"
                }
            }

            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()
            if response.status_code == 200:
                response_info = response_data['response']
                
                alternate_phone_numbers = [phone['phoneNumber'] for phone in response_info['alternatePhone']]
                alternate_phone = next((phone for phone in alternate_phone_numbers if phone != userRole.user.mobile), None)

                email = response_info['email'][0]['email'] if response_info['email'] else None

                addresses = response_info['address'][:2]
                address1 = addresses[0] if len(addresses) > 0 else None
                address2 = addresses[1] if len(addresses) > 1 else None

                pan_card_number = response_info['PAN'][0]['IdNumber'] if response_info['PAN'] else None

                first_name = response_info['name']['firstName'] if 'name' in response_info and 'firstName' in response_info['name'] else None
                last_name = response_info['name']['lastName'] if 'name' in response_info and 'lastName' in response_info['name'] else None

                state = response_info['address'][0]['State'] if response_info['address'] else None
                postal_code = response_info['address'][0]['Postal'] if response_info['address'] else None

                prefill_data = {
                    "alternatePhone": alternate_phone,
                    "email": email,
                    "address1": address1,
                    "address2": address2,
                    "panCardNumber": pan_card_number,
                    "firstName": first_name,
                    "lastName": last_name,
                    "state": state,
                    "postalCode": postal_code
                }

                return JsonResponse({"prefillData": prefill_data,"user" : userRole.id,"phoneNumber":userRole.user.mobile}, status=200)
            # return JsonResponse({"message": "Failed to fetch data from API" ,"response":response.json()}, status=response.status_code)
            return JsonResponse({"prefillData": None ,"user" : userRole.id,"phoneNumber":userRole.user.mobile}, status=200)
        except models.UserRole.DoesNotExist:
            return JsonResponse({"message" : "user ID does not exist"},status=400) 
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET methods are allowed"}, status=405)

@csrf_exempt
def SubmitProfileAPI(request,user=None):
    if request.method == 'POST':
        data = json.loads(request.body)
        userID = data.get('user')

        if not userID:
            return JsonResponse({"message": "userID should be there"}, status=400)

        with transaction.atomic():
            try :
                user_role = models.UserRole.objects.get(id=userID)
                # print(user_role.id)
                if user_role.role == 'Individual':
                    alternatePhone = data.get('alternatePhone')
                    email= data.get('email')
                    address1= data.get('address1')
                    address2= data.get('address2')
                    panCardNumber= data.get('panCardNumber')
                    firstName = data.get('firstName')
                    lastName = data.get('lastName')
                    state = data.get('state')
                    city = data.get('city')
                    postalCode = data.get('postalCode')

                    if not all([alternatePhone, email, address1, address2, firstName, lastName, state,city, postalCode]):
                        return JsonResponse({"message": "All fields are required"}, status=400)

                    user_role.user.email = email
                    user_role.save()

                    try :
                        # update
                        # print("jbdcfh ")
                        individualProfileExistence = models.IndividualDetails.objects.get(user_role=user_role)
                        # print(individualProfileExistence)
                        individualProfileExistence.first_name = firstName
                        individualProfileExistence.last_name = lastName 
                        individualProfileExistence.addressLine1 = address1 
                        individualProfileExistence.addressLine2 = address2 
                        individualProfileExistence.city = city 
                        individualProfileExistence.state = state
                        individualProfileExistence.pin_code = postalCode 
                        individualProfileExistence.alternate_phone_no = alternatePhone 
                        individualProfileExistence.updated_at = timezone.now()
                        individualProfileExistence.save() 
                        
                        try :
                            pancards = models.PanCardNos.objects.get(user_role=user_role)
                            pancards.pan_card_no = panCardNumber
                            pancards.save()
                        except :
                            return JsonResponse({"message":"pan card entery is not there but Individual details is there"},status=400)

                        return JsonResponse({"message" : "Successfully entered individual profile","indiviual_profileID":individualProfileExistence.id , "user" :user_role.id},status=200)

                                #   models.IndividualDetails.DoesNotExist and models.PanCardNos.DoesNotExist == True then only create thase
                    except models.IndividualDetails.DoesNotExist :
                        try:
                            models.PanCardNos.objects.get(user_role=user_role)
                            return JsonResponse({"message": "PAN card already exists but individual profile does not"}, status=400)
                        except models.PanCardNos.DoesNotExist:
                            if not panCardNumber:
                                return JsonResponse({"message": "panCardNumber is required as it is new user"}, status=400)
                        
                            # create
                            individualProfile = models.IndividualDetails.objects.create(
                                user_role = user_role ,
                                first_name = firstName,
                                last_name = lastName ,
                                addressLine1 = address1 ,
                                addressLine2 = address2 ,
                                city = city ,
                                state = state,
                                pin_code = postalCode ,
                                alternate_phone_no = alternatePhone ,
                                created_at = timezone.now() ,
                                updated_at = timezone.now() 
                            )

                            try :
                                pancards = models.PanCardNos.objects.get(user_role=user_role)
                                return JsonResponse({"message":"pan card entery is there"},status=400)
                            except :
                                panCard = models.PanCardNos.objects.create(
                                    user_role = user_role,
                                    pan_card_no = panCardNumber ,
                                    created_at = timezone.now()
                                )
                            return JsonResponse({"message" : "Successfully entered individual profile","indiviual_profileID":individualProfile.id , "panCard_NumberID":panCard.id , "user" :user_role.id},status=200)
                
                elif user_role.role == 'Company':
                    company_name = data.get('company_name')
                    addressLine1 = data.get('addressLine1')
                    addressLine2 = data.get('addressLine2')
                    city = data.get('city')
                    state = data.get('state')
                    email = data.get('email')
                    pin_no = data.get('pin_no')
                    alternate_phone_no = data.get('alternate_phone_no')
                    company_pan_no = data.get('company_pan_no')
                    public_url_company = data.get('public_url_company')

                    if not all([company_name, addressLine1, addressLine2, city, state ,email, pin_no, alternate_phone_no, public_url_company]):
                        return JsonResponse({"message": "All fields are required"}, status=400)

                    user_role.user.email = email
                    user_role.save()

                    try :
                        companyProfileExistence = models.CompanyDetails.objects.get(user_role=user_role)
                        # update
                        companyProfileExistence.company_name = company_name
                        companyProfileExistence.addressLine1 = addressLine1
                        companyProfileExistence.addressLine2 = addressLine2
                        companyProfileExistence.city = city
                        companyProfileExistence.state  = state
                        companyProfileExistence.pin_no = pin_no
                        companyProfileExistence.alternate_phone_no = alternate_phone_no
                        companyProfileExistence.public_url_company = public_url_company
                        companyProfileExistence.updated_at = timezone.now()
                        companyProfileExistence.save()

                        try :
                            pancards = models.PanCardNos.objects.get(user_role=user_role)
                            pancards.pan_card_no = panCardNumber
                            pancards.save()
                        except :
                            return JsonResponse({"message":"pan card entery is not there but company details is there"},status=400)
                        
                        return JsonResponse({"message" : "Successfully entered company profile","company_ProfileID":companyProfileExistence.id , "user" :user_role.id},status=200)
                    except models.CompanyDetails.DoesNotExist:
                        try:
                            models.PanCardNos.objects.get(user_role=user_role)
                            return JsonResponse({"message": "PAN card already exists but company profile does not"}, status=400)
                        except models.PanCardNos.DoesNotExist:
                            if not panCardNumber:
                                return JsonResponse({"message": "panCardNumber is required as it is new user"}, status=400)
                            # create
                            companyProfile = models.CompanyDetails.objects.create(
                                user_role = user_role ,
                                company_name = company_name ,
                                addressLine1 = addressLine1 ,
                                addressLin2 = addressLine2,
                                city = city,
                                state = state,
                                pin_no = pin_no ,
                                alternate_phone_no = alternate_phone_no,
                                public_url_company = public_url_company ,
                                created_at = timezone.now() ,
                                updated_at = timezone.now()
                            )

                            try :
                                pancards = models.PanCardNos.objects.get(user_role=user_role)
                                return JsonResponse({"message":"pan card entery is there"},status=400)
                            except :
                                panCard = models.PanCardNos.objects.create(
                                    user_role = user_role,
                                    pan_card_no = panCardNumber ,
                                    created_at = timezone.now()
                                )

                            return JsonResponse({"message" : "Successfully entered company profile","company_ProfileID":companyProfile.id , "panCard_NumberID":panCard.id,"user" :user_role.id},status=200)
                else :
                    return JsonResponse({"message" : "Role is not matched"},status=400)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message":"userID does not found"},status=400)
    
    elif request.method == 'GET':
        # userID = request.GET.get('user')

        if not user:
            return JsonResponse({"message": "userID should be there"}, status=400)

        try:
            user_role = models.UserRole.objects.get(id=user)
            response_data = {
                "user": {
                    "id": user_role.id,
                    "email": user_role.user.email,
                    "mobile" : user_role.user.mobile,
                    "role": user_role.role,
                }
            }

            if user_role.role == 'Individual':
                try:
                    individual_details = models.IndividualDetails.objects.get(user_role=user_role)
                    response_data["profile"] = {
                        "first_name": individual_details.first_name,
                        "last_name": individual_details.last_name,
                        "addressLine1": individual_details.addressLine1,
                        "addressLine2": individual_details.addressLine2,
                        "city": individual_details.city,
                        "state": individual_details.state,
                        "pin_code": individual_details.pin_code,
                        "alternate_phone_no": individual_details.alternate_phone_no,
                    }
                except models.IndividualDetails.DoesNotExist:
                    return JsonResponse({"message": "Individual profile not found"}, status=404)

            elif user_role.role == 'Company':
                try:
                    company_details = models.CompanyDetails.objects.get(user_role=user_role)
                    response_data["profile"] = {
                        "company_name": company_details.company_name,
                        "addressLine1": company_details.addressLine1,
                        "addressLine2": company_details.addressLine2,
                        "city": company_details.city,
                        "state": company_details.state,
                        "pin_no": company_details.pin_no,
                        "alternate_phone_no": company_details.alternate_phone_no,
                        "public_url_company": company_details.public_url_company,
                    }
                except models.CompanyDetails.DoesNotExist:
                    return JsonResponse({"message": "Company profile not found"}, status=404)

            return JsonResponse(response_data, status=200)
        except models.UserRole.DoesNotExist:
            return JsonResponse({"message": "user does not found"}, status=400)
    else:
        return JsonResponse({"message": "Only POST methods are allowed"}, status=405)
    
@csrf_exempt
def BankAccDetailsAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_role_id = data.get('user')

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

                return JsonResponse({"message": "Bank account details saved successfully", "bank_account_id": bank_account_details.id,"user" :user_role.id}, status=201)

            except KeyError:
                return JsonResponse({"message": "Missing required fields"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

    # elif request.method == 'GET':
    #     try:
    #         data = json.loads(request.body)
    #         user_role_id = data.get('user_r')
    #         print(user_role_id)

    #         if not user_role_id:
    #             return JsonResponse({"message": "user_role_id is required"}, status=400)

    #         try:
    #             user_role = models.UserRole.objects.get(id=user_role_id)
    #             print(user_role)
    #         except models.UserRole.DoesNotExist:
    #             return JsonResponse({"message": "User role not found"}, status=404)

    #         bank_accounts = models.BankAccountDetails.objects.filter(user_role=user_role)
    #         print(bank_accounts.count())
    #         if not bank_accounts.exists():
    #             return JsonResponse({"message": "No bank accounts found for this user role"}, status=404)

    #         account_numbers = [{"bank_account_id": acc.id, "account number ending with": str(acc.account_number)[-4:]} for acc in bank_accounts]
    #         return JsonResponse({"bank_accounts": account_numbers}, status=200)

    #     except Exception as e:
    #         return JsonResponse({"message": str(e)}, status=500)

    else:
        return JsonResponse({"message": "Only POST methods are allowed"}, status=405)

@csrf_exempt
def Credit_FundsAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_role_id = data.get('user')
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
            
            with transaction.atomic():
                try:
                    wallet = models.OutstandingBalance.objects.get(bank_acc=bank_account)
                    wallet.balance += amount
                    wallet.updated_at = timezone.now().date()
                    wallet.save()
                except models.OutstandingBalance.DoesNotExist:
                    wallet = models.OutstandingBalance.objects.create(
                        bank_acc=bank_account,
                        balance=amount,
                        updated_at=timezone.now().date()
                    )

                Balancetransaction = models.OutstandingBalanceTransaction.objects.create(
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

                return JsonResponse({
                        "message": "Funds added successfully",
                        "user" :user_role.id,
                        "wallet_balance": wallet.balance,
                        "transaction_id": Balancetransaction.transaction_id
                }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)

@csrf_exempt
def LedgerAPI(request, user):
    if request.method == 'GET':
        try:
            try:
                user_role = models.UserRole.objects.get(id=user)
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
                    "invoice": transaction.invoice.product_name if transaction.invoice else None,
                    "time_date": transaction.time_date,
                })

            total_balance = sum(wallet.balance for wallet in wallets)

            return JsonResponse({"transactions": transactions_data, "Balance": total_balance , "user" : user_role.id}, status=200)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET method is allowed"}, status=405)
    
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

@csrf_exempt
def GetDetails(request, user):
    if request.method == 'GET':
        try:
            try:
                userRole = models.UserRole.objects.get(id=user)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "user_role_id doesn't exist"}, status=400)

            invoices = models.Invoices.objects.filter(expired=False)

            invoice_data_list = []

            for invoice in invoices:
                post_for_sales = models.Post_for_sale.objects.filter(invoice_id = invoice ,sold=False,remaining_units__gt=0)
                for post_for_sale in post_for_sales:
                        if post_for_sale.user_id == userRole:
                            break
                        invoice_data = {
                            'id': invoice.id,
                            'Invoice_id': invoice.invoice_id,
                            'Invoice_primary_id': invoice.primary_invoice_id,
                            'Invoice_no_of_units': post_for_sale.no_of_units,
                            'post_for_sellID' : post_for_sale.id,
                            'Invoice_remaining_units': post_for_sale.remaining_units,
                            'Invoice_per_unit_price': post_for_sale.per_unit_price,
                            'Invoice_name': invoice.product_name,
                            'Invoice_post_date': post_for_sale.post_date,
                            'Invoice_post_time': post_for_sale.post_time,
                            'Invoice_interest': invoice.interest,
                            'Invoice_xirr': invoice.xirr,
                            'Invoice_irr': invoice.irr,
                            'Invoice_from_date' : post_for_sale.from_date,
                            'Invoice_to_date' : post_for_sale.to_date ,
                            'Invoice_tenure_in_days': invoice.tenure_in_days,
                            'Invoice_expiration_time': invoice.expiration_time,
                            'Invoice_sold': invoice.is_fractionalized,
                            'isAdmin': post_for_sale.user_id.user.is_admin,
                            'type': 'CanBuy'
                        }
                        invoice_data_list.append(invoice_data)

            buyers = models.Buyers.objects.filter(user_id=userRole)
            for buyer in buyers:
                buyer_units = models.Buyer_UnitsTracker.objects.filter(buyer_id=buyer)
                # has_posted_for_sale = buyer_units.filter(post_for_saleID__isnull=False).exists()

                # 1 -> yes flag = 1   flag = 1                         flag = 2
                # 2 -> yes flag = 1   flag = 1                         means this is posted for sale
                # 3 -> yes flag = 1   flag = 2
                # 4 -> yes flag = 2   means this is posted for sale
                #  means this is posted for sale

                # flag == 2 -> buyer posted for sale
                # flag == 1 -> buyer not posted for sale
                
                for buyer_unit in buyer_units:
                    if buyer_unit.post_for_saleID == None:
                        flag =1
                    else :
                        flag = 2
                        break
                if flag == 2:  #posted
                    # first_unit = buyer_units.first()
                    # invoice = first_unit.unitID.invoice
                    invoice_data = {
                        'id': invoice.id,
                        'Invoice_id': invoice.invoice_id,
                        'Invoice_primary_id': invoice.primary_invoice_id,
                        'Buyer_id': buyer.id,
                        'Invoice_no_of_units': buyer.no_of_units,
                        'Invoice_remaining_units': buyer.no_of_units,
                        'Invoice_per_unit_price': buyer.per_unit_price_invested,
                        'Invoice_name': invoice.product_name,
                        'Invoice_post_date': buyer.purchase_date,
                        'Invoice_post_time': buyer.purchase_time,
                        'Invoice_interest': invoice.interest,
                        'Invoice_xirr': invoice.xirr,
                        'Invoice_irr': invoice.irr,
                        'Invoice_tenure_in_days': invoice.tenure_in_days,
                        'Invoice_expiration_time': invoice.expiration_time,
                        'isAdmin': buyer.user_id.user.is_admin,
                        'Buyer_user_id' : buyer.user_id.user.id ,
                        'type': 'PostedForSale'
                    }
                    invoice_data_list.append(invoice_data)

                if flag == 1:  #not posted
                    # first_unit = buyer_units.first()
                    # invoice = first_unit.unitID.invoice
                    invoice_data = {
                        'id': invoice.id,
                        'Invoice_id': invoice.invoice_id,
                        'Invoice_primary_id': invoice.primary_invoice_id,
                        'Buyer_id': buyer.id,
                        'Invoice_no_of_units': buyer.no_of_units,
                        'Invoice_remaining_units': buyer.no_of_units,
                        'Invoice_per_unit_price': buyer.per_unit_price_invested,
                        'Invoice_name': invoice.product_name,
                        'Invoice_post_date': buyer.purchase_date,
                        'Invoice_post_time': buyer.purchase_time,
                        'Invoice_interest': invoice.interest,
                        'Invoice_xirr': invoice.xirr,
                        'Invoice_irr': invoice.irr,
                        'Invoice_tenure_in_days': invoice.tenure_in_days,
                        'Invoice_expiration_time': invoice.expiration_time,
                        'isAdmin': buyer.user_id.user.is_admin,
                        'Buyer_user_id' : buyer.user_id.user.id ,
                        'type': 'Brought'
                    }
                    invoice_data_list.append(invoice_data)

                # if not has_posted_for_sale:
                #     first_unit = buyer_units.first()
                #     invoice = first_unit.unitID.invoice
                #     invoice_data = {
                #         'id': invoice.id,
                #         'Invoice_id': invoice.invoice_id,
                #         'Invoice_primary_id': invoice.primary_invoice_id,
                #         'Buyer_id': first_unit.buyer_id.id,
                #         'Invoice_no_of_units': first_unit.buyer_id.no_of_units,
                #         'Invoice_remaining_units': first_unit.buyer_id.no_of_units,
                #         'Invoice_per_unit_price': first_unit.buyer_id.per_unit_price_invested,
                #         'Invoice_name': invoice.product_name,
                #         'Invoice_post_date': first_unit.buyer_id.purchase_date,
                #         'Invoice_post_time': first_unit.buyer_id.purchase_time,
                #         'Invoice_interest': invoice.interest,
                #         'Invoice_xirr': invoice.xirr,
                #         'Invoice_irr': invoice.irr,
                #         'Invoice_tenure_in_days': invoice.tenure_in_days,
                #         'Invoice_expiration_time': invoice.expiration_time,
                #         'Invoice_sold': invoice.is_fractionalized,
                #         'Invoice_posted_for_sale': has_posted_for_sale,
                #         'isAdmin': False,
                #         'type': 'Bought'
                #     }
                #     invoice_data_list.append(invoice_data)

            return JsonResponse({"invoices": invoice_data_list , "user" : userRole.id}, status=200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET method is allowed"}, status=405)

@csrf_exempt
def TobuyAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            userRoleID = data.get('user')
            postForSaleID = data.get('postForSaleID')
            no_of_units = data.get('no_of_units')

            try:
                user_role = models.UserRole.objects.get(id=userRoleID)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User not found"}, status=404)

            try:
                bankAcc = models.BankAccountDetails.objects.get(user_role=user_role)
                buyer_wallet = models.OutstandingBalance.objects.get(bank_acc=bankAcc)
            except models.OutstandingBalance.DoesNotExist:
                return JsonResponse({"message": "Buyer Wallet not found"}, status=404)
            
            try:
                postForSale = models.Post_for_sale.objects.get(id=postForSaleID)
            except models.Post_for_sale.DoesNotExist:
                return JsonResponse({"message": "postForSaleID not found"}, status=404)
            
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
                        unitID=unit.unitID
                    )

                    models.Sales_UnitTracker.objects.create(
                        unitID=unit.unitID,
                        sellersID=sales
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
                    invoice = postForSale.invoice_id ,
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
                    invoice = postForSale.invoice_id,
                    time_date = timezone.now()
                )

                postForSale.remaining_units -= no_of_units
                postForSale.save()

                if postForSale.remaining_units == 0:
                    postForSale.sold= True

            return JsonResponse({"message": "Units bought successfully", "buyer_id": buyer.id,"user" : user_role.id}, status=201)        
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
            userRoleID = data.get('user')
            buyerID = data.get('buyerID')
            no_of_units = data.get('no_of_units')
            per_unit_price = data.get('per_unit_price')
            from_date = data.get('from_date')
            to_date = data.get('to_date')

            if not all([userRoleID, no_of_units, per_unit_price]):
                return JsonResponse({"message": "All fields are required"}, status=400)

            try:
                user_role = models.UserRole.objects.get(id=userRoleID)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found"}, status=404)

            try:
                buyer = models.Buyers.objects.get(id=buyerID)
            except models.Buyers.DoesNotExist:
                return JsonResponse({"message": "Buyer not found"}, status=404)

            with transaction.atomic():

                try :
                    buyer_Units = models.Buyer_UnitsTracker.objects.filter(buyer_id=buyer , post_for_saleID = None).order_by('id')[:no_of_units]
                except models.Buyer_UnitsTracker.DoesNotExist:
                    return JsonResponse({"message" : "buyer unit does not exits or Not sufficient units for post for sale"},status=400)
                
                if buyer_Units.count() < no_of_units:
                    return JsonResponse({"message": "Not enough units available for selling"}, status=400)
            
                for buyer_unit in buyer_Units:
                    invoice = buyer_unit.unitID.invoice
                    break

                post_for_sale = models.Post_for_sale.objects.create(
                    no_of_units = no_of_units ,
                    per_unit_price = per_unit_price ,
                    user_id = user_role ,
                    invoice_id = invoice ,
                    remaining_units = no_of_units ,
                    withdrawn = False ,
                    post_time = timezone.now().time() ,
                    post_date = timezone.now().date() ,
                    from_date = from_date ,
                    to_date = to_date ,
                    sold = False ,
                    post_dateTime = timezone.now() ,
                    is_admin =  user_role.user.is_admin 
                )

                for buyer_unit in buyer_Units:
                    buyer_unit.post_for_saleID = post_for_sale
                    buyer_unit.save()

                    models.Post_For_Sale_UnitTracker.objects.create(
                        unitID=buyer_unit.unitID,
                        post_for_saleID=post_for_sale
                    )
                return JsonResponse({"message": "Sell transaction recorded successfully", "user": user_role.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)

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
def cashFlowAPI(request,invoiceID):
    if request.method == 'GET':
        try :
            try:
                invoice =  models.Invoices.objects.get(id = invoiceID)
            except models.Invoices.DoesNotExist:
                return JsonResponse({"message":"invoiceID not found"})
            
            primary_invoice_id = invoice.primary_invoice_id
            print(primary_invoice_id)
            url = 'http://backend.ethyx.in/admin-api/payment-schedule-calculator/'
            headers = {
                'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIyMzQyNzUwLCJpYXQiOjE3MjIyNTYzNTAsImp0aSI6ImZlMjAwMzM1OTYzNjRmNTRhYjA3ZTE4NWU4ZDI5NWJkIiwidWlkIjoiQVNOV1ROODI4NSJ9.8_yy4cwJGrJ8z2UsRcAYl7Hr3-1xGfIGoY4TFQ3JZng',
                'Content-Type': 'application/json'
            }

            payload = {
                "invoice_product_id": 8
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                return JsonResponse({
                        "CashFlow" : response.json()
                }, status=200)
            else:
                return JsonResponse({"message": response.json()}, status=response.status_code)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)
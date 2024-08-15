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
from collections import defaultdict

@csrf_exempt
def GenerateOtpAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            country_code = data.get('countryCode')
            mobile_number = data.get('mobileNumber')

            if not country_code or not mobile_number:
                return JsonResponse({"message": "countryCode and mobileNumber are required"}, status=400)

            # url = 'https://api-preproduction.signzy.app/api/v3/phone/generateOtp'
            
            # headers = {
            #     'Authorization': 'lWQdJDRWrlibgEbU3O53UXXQSYnQQGhF',
            #     'Content-Type': 'application/json'
            # }

            # payload = {
            #     "countryCode": country_code,
            #     "mobileNumber": mobile_number
            # }

            # response = requests.post(url, headers=headers, json=payload)
            # print(response.json)
            status= 200
            # if response.status_code == 200:
            if status == 200:
                # return JsonResponse({"result": response.json()}, status=200)
                return JsonResponse({"result": {"result" : {"referenceId" : "telecom_15JaOVZRiuXsoSPoqiwjSDjpDWoH5cg8"}}}, status=200)
            else:
                # return JsonResponse({"message": response.json()}, status=response.status_code)
                return JsonResponse({"message": "Inavalid Number"}, status=500)
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
            # otp = 575244
            extra_fields = data.get('extraFields')
            user_role = data.get('user_role')

            if not all([country_code, mobile_number, user_role ,reference_id, otp, str(extra_fields)]):
                return JsonResponse({"message": "All fields are required"}, status=400)

            # url = 'https://api-preproduction.signzy.app/api/v3/phone/getNumberDetails'
            # headers = {
            #     'Authorization': 'lWQdJDRWrlibgEbU3O53UXXQSYnQQGhF',
            #     'Content-Type': 'application/json'
            # }

            # payload = {
            #     "countryCode": country_code,
            #     "mobileNumber": mobile_number,
            #     "referenceId": reference_id,
            #     "otp": otp,
            #     "extraFields": extra_fields
            # }

            # response = requests.post(url, headers=headers, json=payload)
            status_code = 200
            with transaction.atomic():
                # if response.status_code == 200:
                if status_code == 200:
                    try:
                        user = models.User.objects.get(mobile = mobile_number)
                        userRole = models.UserRole.objects.get(user = user)
                        if userRole.role != user_role:
                            return JsonResponse({"message":"user role is not match"},status=400)
                        return JsonResponse({
                                "message": "User already registered",
                                # "signzy_Response" : response.json(),
                                "user": userRole.id,
                                "user_role" : userRole.role,
                                "is_admin" : userRole.user.is_admin,
                                "is_superadmin" : userRole.user.is_superadmin
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
                                # "signzy_Response" : response.json(),
                                "user": userRole.id,
                                "user_role" : userRole.role,
                                "is_admin" : userRole.user.is_admin,
                                "is_superadmin" : userRole.user.is_superadmin
                            }, status=201)
                    except models.UserRole.DoesNotExist:
                        userRole = models.UserRole.objects.create(user=user,role=user_role)
                        if userRole.role != user_role:
                            return JsonResponse({"message":"user role is not match"},status=400)
                        return JsonResponse({
                                "message": "User already registered",
                                # "signzy_Response" : response.json(),
                                "user": userRole.id,
                                "user_role" : userRole.role,
                                "is_admin" : userRole.user.is_admin,
                                "is_superadmin" : userRole.user.is_superadmin
                            }, status=200)
                    except Exception as e:
                        return JsonResponse({"message": str(e)}, status=500)
                else:
                    # return JsonResponse({"message": response.json()}, status=response.status_code)
                    return JsonResponse({"message": "signzy"}, status=500)
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
                    try :
                        wallet = models.Wallet.objects.get(user_role=userRole)
                        OutstandingBalance = wallet.OutstandingBalance
                    except :
                        OutstandingBalance = 0
                else :
                    is_BankDetailsExists = False
                    OutstandingBalance = 0

            elif userRole.role == 'Company' :
                Company_Detials_exist = models.CompanyDetails.objects.filter(user_role=userRole).exists()
                BankAcc_Details_exist = models.BankAccountDetails.objects.filter(user_role=userRole).exists()
                if Company_Detials_exist :
                    is_KYC = True
                else :
                    is_KYC = False
                if BankAcc_Details_exist :
                    is_BankDetailsExists = True
                    try :
                        wallet = models.Wallet.objects.get(user_role=userRole)
                        OutstandingBalance = wallet.OutstandingBalance
                    except :
                        OutstandingBalance = 0
                else :
                    is_BankDetailsExists = False
                    OutstandingBalance = 0

            return JsonResponse({"is_KYC": is_KYC , 
                                 "is_BankDetailsExists":is_BankDetailsExists,
                                 "user": userRole.id  , 
                                 'user_role' : userRole.role , 
                                 'phone' : userRole.user.mobile ,
                                 "is_admin" : str(userRole.user.is_admin) , 
                                 "is_superAdmin" : str(userRole.user.is_superadmin),
                                 "OutstandingBalance" : OutstandingBalance },status=200)
        
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

            if userRole.role == "Individual":
                url = 'https://api-preproduction.signzy.app/api/v3/phonekyc/phone-prefill-v2'
                headers = {
                    'Authorization': 'lWQdJDRWrlibgEbU3O53UXXQSYnQQGhF',
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

                    return JsonResponse({"prefillData": prefill_data,
                                         "user" : userRole.id,
                                         "phoneNumber":userRole.user.mobile}, status=200)
                # return J  sonResponse({"message": "Failed to fetch data from API" ,"response":response.json()}, status=response.status_code)
                return JsonResponse({"prefillData": None ,"user" : userRole.id,"phoneNumber":userRole.user.mobile}, status=200)
            else :
                data = json.loads(request.body)
                gstin = data.get('gstin')

                try :
                    gstin_check = models.GSTIN_Nos.objects.get(user_role = userRole)
                    return JsonResponse({"message": "already GSTIN no is there",
                                         "user" : userRole.id,
                                         "phoneNumber":userRole.user.mobile,
                                         "GSTIN" : gstin_check.GSTIN_no,
                                         "GSTIN_ID" : gstin_check.id}, status=200)
                except models.GSTIN_Nos.DoesNotExist:
                    with transaction.atomic():
                        gstin = models.GSTIN_Nos.objects.create(
                            user_role = userRole ,
                            GSTIN_no = gstin ,
                            created_at = timezone.now()
                        )
                        url = 'https://api-preproduction.signzy.app/api/v3/gst/search'

                        headers = {
                            'Authorization': 'lWQdJDRWrlibgEbU3O53UXXQSYnQQGhF',
                            'Content-Type': 'application/json'
                        }
                        payload = {
                            "gstin" : gstin,
                            "returnFilingFrequency" : True
                        }
                        response = requests.post(url, headers=headers, json=payload)
                        response_data = response.json()
                        if response.status_code == 200:

                            gstn_detailed = data['result']['gstnDetailed']
                            gstn_records = data['result']['gstnRecords'][0]

                            legal_name_of_business = gstn_detailed.get('legalNameOfBusiness', '')
                            trade_name_of_business = gstn_detailed.get('tradeNameOfBusiness', '')
                            principal_place_address = gstn_detailed.get('principalPlaceAddress', '')
                            additional_place_address = gstn_detailed.get('additionalPlaceAddress', '')

                            principal_place_split_address = gstn_detailed.get('principalPlaceSplitAddress', {})
                            principal_state = principal_place_split_address.get('state', [['']])[0][0]
                            principal_city = principal_place_split_address.get('city', [''])[0]
                            principal_pincode = principal_place_split_address.get('pincode', '')

                            additional_place_split_address = gstn_detailed.get('additionalPlaceSplitAddress', {})
                            additional_state = additional_place_split_address.get('state', [['']])[0][0]
                            additional_city = additional_place_split_address.get('city', [''])[0]
                            additional_pincode = additional_place_split_address.get('pincode', '')

                            email_id = gstn_records.get('emailId', '')
                            mob_num = gstn_records.get('mobNum', '')

                            # Printing the extracted values
                            print(f"Legal Name of Business: {legal_name_of_business}")
                            print(f"Trade Name of Business: {trade_name_of_business}")
                            print(f"Principal Place Address: {principal_place_address}")
                            print(f"Additional Place Address: {additional_place_address}")
                            print(f"Principal State: {principal_state}")
                            print(f"Principal City: {principal_city}")
                            print(f"Principal Pincode: {principal_pincode}")
                            print(f"Additional State: {additional_state}")
                            print(f"Additional City: {additional_city}")
                            print(f"Additional Pincode: {additional_pincode}")
                            print(f"Email ID: {email_id}")
                            print(f"Mobile Number: {mob_num}")

                            prefill_data = {
                                "company_name" : legal_name_of_business,
                                "address1" :  principal_place_address ,
                                "address2" : additional_place_address ,
                                "city" : principal_city ,
                                "state" : additional_state ,
                                "postalCode" : principal_pincode ,
                                "alternate_phone_no" : mob_num ,
                                "public_url_company" : None ,
                                "email": email,
                                "panCardNumber": None
                            }

                            return JsonResponse({"prefillData": prefill_data ,
                                                "user" : userRole.id,
                                                "phoneNumber":userRole.user.mobile}, status=200)
                        return JsonResponse({"prefillData": None ,
                                         "user" : userRole.id,
                                         "phoneNumber":userRole.user.mobile}, status=200)
        except models.UserRole.DoesNotExist:
            return JsonResponse({"message" : "user ID does not exist"},status=400) 
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET methods are allowed"}, status=405)

@csrf_exempt
def ProfileAPI(request,user=None):
    if request.method == 'POST':
        data = json.loads(request.body)
        userID = data.get('user')

        if not userID:
            return JsonResponse({"message": "userID should be there"}, status=400)

        with transaction.atomic():
            try :
                user_role = models.UserRole.objects.get(id=userID)
                user = user_role.user
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
                    
                    print("email",email)
                    user.email = email
                    user.save()
                    print("userRole.user.email" ,user_role.user.email)

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

                    user.email = email
                    user.save()

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
                            pancards.pan_card_no = company_pan_no
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
                                    pan_card_no = company_pan_no ,
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
                    return JsonResponse({"message": "Individual profile not found"}, status=400)

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
                    return JsonResponse({"message": "Company profile not found"}, status=400)

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
                return JsonResponse({"message": "user is required"}, status=400)

            try:
                user_role = models.UserRole.objects.get(id=user_role_id)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found"}, status=400)

            try:
                # following details will come from 3rd party api
                account_number = data.get('account_number')
                ifc_code = data.get('ifc_code')
                account_type = data.get('account_type')

                if not account_number or not ifc_code or not account_type:
                    return JsonResponse({"message": "account_number, ifc_code, and account_type are required"}, status=400)
                
                is_exists = models.BankAccountDetails.objects.filter(user_role=user_role).exists()

                if is_exists :
                    bank_account_details = models.BankAccountDetails.objects.create(
                        user_role=user_role,
                        account_number=account_number,
                        ifc_code=ifc_code,
                        account_type=account_type
                     )
                    try :
                        wallet = models.Wallet.objects.get(user_role=user_role)
                    except models.Wallet.DoesNotExist:
                        wallet = models.Wallet.objects.create(
                            user_role=user_role,
                            primary_bankID=bank_account_details,
                            OutstandingBalance = 0,
                            updated_at=timezone.now()
                            )
                    return JsonResponse({"message": "Bank account details saved successfully", "bank_account_id": bank_account_details.id,"user" :user_role.id,"primary_bank":wallet.primary_bankID.id,"primary_bank_AccNo":wallet.primary_bankID.account_number}, status=200)
                else :
                    # ek bhi nai hoi 
                    bank_account_details = models.BankAccountDetails.objects.create(
                        user_role=user_role,
                        account_number=account_number,
                        ifc_code=ifc_code,
                        account_type=account_type
                     )
                    try :
                        wallet = models.Wallet.objects.get(user_role=user_role)
                    except models.Wallet.DoesNotExist:
                        wallet = models.Wallet.objects.create(
                            user_role=user_role,
                            primary_bankID=bank_account_details,
                            OutstandingBalance = 0,
                            updated_at=timezone.now()
                            )
                    return JsonResponse({"message": "Bank account details saved successfully", "bank_account_id": bank_account_details.id,"user" :user_role.id,"primary_bank":wallet.primary_bankID.id,"primary_bank_AccNo":wallet.primary_bankID.account_number}, status=201)
            except json.JSONDecodeError:
                return JsonResponse({"message": "Invalid JSON"}, status=400)
            except Exception as e:
                return JsonResponse({"message": str(e)}, status=500)
            except KeyError:
                return JsonResponse({"message": "Missing required fields"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
                return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only POST methods are allowed"}, status=405)

@csrf_exempt
def Credit_FundsAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_role_id = data.get('user')
            amount = data.get('amount')

            if not user_role_id  or not amount:
                return JsonResponse({"message": "user_role_id, bank_acc_id, and amount are required"}, status=400)

            try:
                user_role = models.UserRole.objects.get(id=user_role_id)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found"}, status=400)

            try:
                wallet = models.Wallet.objects.get(user_role=user_role)
            except models.BankAccountDetails.DoesNotExist:
                return JsonResponse({"message": " Wallet not found for the given user"}, status=400)
            
            with transaction.atomic():
                try:
                    wallet.OutstandingBalance += amount
                    wallet.updated_at = timezone.now().date()
                    wallet.save()
                except models.Wallet.DoesNotExist:
                    return JsonResponse({"message": " Wallet not found for the given user"}, status=400)

                Balancetransaction = models.WalletTransaction.objects.create(
                        wallet=wallet,
                        transaction_id=uuid.uuid4(),
                        type='fund',
                        creditedAmount=amount,
                        debitedAmount=None,
                        status='response',
                        source='bank_to_wallet',
                        purpose='Funds added to wallet',
                        from_bank_acc = wallet.primary_bankID,
                        to_wallet = wallet,
                        invoice=None,
                        time_date=timezone.now()
                    )

                return JsonResponse({
                        "message": "Funds added successfully",
                        "user" :user_role.id,
                        "wallet_balance": wallet.OutstandingBalance,
                        "primary_BankAccID" : wallet.primary_bankID.id,
                        "primary_BankAccNo" : wallet.primary_bankID.account_number,
                        "transaction_id": Balancetransaction.transaction_id
                }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)

@csrf_exempt
def Withdraw_FundsAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_role_id = data.get('user')
            amount = data.get('amount')

            if not user_role_id  or not amount:
                return JsonResponse({"message": "user and amount are required"}, status=400)

            try:
                user_role = models.UserRole.objects.get(id=user_role_id)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User not found"}, status=400)

            try:
                wallet = models.Wallet.objects.get(user_role=user_role)
            except models.BankAccountDetails.DoesNotExist:
                return JsonResponse({"message": " Wallet not found for the given user"}, status=400)
            
            with transaction.atomic():
                try:
                    if wallet.OutstandingBalance < amount:
                        return JsonResponse({"message": "Not sufficient amount to do withdrawal"}, status=400)
                    wallet.OutstandingBalance -= amount
                    wallet.updated_at = timezone.now().date()
                    wallet.save()
                except models.Wallet.DoesNotExist:
                    return JsonResponse({"message": " Wallet not found for the given user"}, status=400)

                Balancetransaction = models.WalletTransaction.objects.create(
                        wallet=wallet,
                        transaction_id=uuid.uuid4(),
                        type='Withdraw',
                        creditedAmount=None,
                        debitedAmount=amount,
                        status='response',
                        source='wallet_to_bank',
                        purpose='Funds debited from wallet',
                        to_bank_acc = wallet.primary_bankID,
                        from_wallet = wallet,
                        invoice=None,
                        time_date=timezone.now()
                    )

                return JsonResponse({
                        "message": "Funds debited successfully",
                        "user" :user_role.id,
                        "wallet_balance": wallet.OutstandingBalance,
                        "primary_BankAccID" : wallet.primary_bankID.id,
                        "primary_BankAccNo" : wallet.primary_bankID.account_number,
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
                return JsonResponse({"message": "User role not found"}, status=400)

            wallet = models.Wallet.objects.filter(user_role=user_role)
            if not wallet.exists():
                return JsonResponse({"message": "No wallets found for this user role"}, status=400)

            transactions = models.WalletTransaction.objects.filter(wallet__in=wallet).order_by('-time_date')

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
                    "from_bank_acc": transaction.from_bank_acc.account_number if transaction.from_bank_acc else None,
                    "to_bank_acc" :transaction.to_bank_acc.account_number if transaction.to_bank_acc else None,
                    "from_wallet" :transaction.from_wallet.id if transaction.from_wallet else None ,
                    "to_wallet" : transaction.to_wallet.id if transaction.to_wallet else None,
                    "invoice": transaction.invoice.product_name if transaction.invoice else None,
                    "time_date": transaction.time_date,
                })

                Balancewallet = wallet.first()
            return JsonResponse({"transactions": transactions_data, "Balance": Balancewallet.OutstandingBalance , "user" : user_role.id}, status=200)

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
                return JsonResponse({"message":"User or bank account doesn't exist"},status=400)
            balance = models.OutstandingBalance.objects.get(bank_acc= bank_acc).balance
            return JsonResponse({"Balance":balance},status = 200)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only GET method is allowed"}, status=405)

@csrf_exempt
def GetSellPurchaseDetailsAPI(request, user):
    if request.method == 'GET':
        try:
            try:
                userRole = models.UserRole.objects.get(id=user)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "user doesn't exist"}, status=400)

            invoices = models.Invoices.objects.filter(expired=False)

            invoice_data_list = []

            for invoice in invoices:
                post_for_sales = models.Post_for_sale.objects.filter(invoice_id = invoice ,sold=False,remaining_units__gt=0).exclude(user_id=userRole)
                for post_for_sale in post_for_sales:
                        invoice_data = {
                            'id': invoice.id,
                            'Invoice_id': invoice.invoice_id,
                            'Invoice_primary_id': invoice.primary_invoice_id,
                            'Invoice_no_of_units': post_for_sale.no_of_units,
                            'post_for_sellID' : post_for_sale.id,
                            'Invoice_remaining_units': post_for_sale.remaining_units,
                            'Invoice_per_unit_price': post_for_sale.per_unit_price,
                            'Invoice_total_price' : post_for_sale.total_price ,
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
                            'isAdmin': post_for_sale.user_id.user.is_admin,
                            'type': 'CanBuy'
                        }
                        invoice_data_list.append(invoice_data)

            buyers = models.Buyers.objects.filter(user_id=userRole)

            for buyer in buyers:
                # not posted for sale
                buyer_units = models.Buyer_UnitsTracker.objects.filter(buyer_id=buyer,post_for_saleID__isnull=True)
                buyer_units_count = buyer_units.count()
                print("buyer_units_count : ",buyer_units_count)
                if buyer_units_count > 0:
                    brought_invoice = buyer_units.first().unitID.invoice 
                    invoice_data = {
                        'id': brought_invoice.id,
                        'Invoice_id': brought_invoice.invoice_id,
                        'Invoice_primary_id': brought_invoice.primary_invoice_id,
                        'Buyer_id': buyer.id,
                        'Purchased_no_of_units': buyer.no_of_units,
                        'Purchased_remaining_units': buyer_units_count,
                        'Purchased_per_unit_price': buyer.per_unit_price_invested,
                        'Invoice_name': brought_invoice.product_name,
                        'Purchased_date': buyer.purchase_date,
                        'Purchased_time': buyer.purchase_time,
                        'Invoice_interest': brought_invoice.interest,
                        'Invoice_xirr': brought_invoice.xirr,
                        'Invoice_irr': brought_invoice.irr,
                        'Invoice_tenure_in_days': brought_invoice.tenure_in_days,
                        'Invoice_expiration_time': brought_invoice.expiration_time,
                        'isAdmin': buyer.user_id.user.is_admin,
                        'Buyer_user_id': buyer.user_id.id,
                        'type': 'Brought'
                    }
                    invoice_data_list.append(invoice_data)

                print("invoice_data_list : ",invoice_data_list)
                
                # posted for sale
                buyer_units_posted_for_sale = models.Buyer_UnitsTracker.objects.filter(buyer_id=buyer, post_for_saleID__isnull=False)
                print("buyer_units_posted_for_sale.count() :",buyer_units_posted_for_sale.count())
                buyer_units_posted_for_sale_count = buyer_units_posted_for_sale.count()
                if buyer_units_posted_for_sale_count > 0:
                    print("bjcvdsuj")
                    # Group the units by post_for_saleID
                    units_by_post_for_sale = defaultdict(list)
                    for unit in buyer_units_posted_for_sale:
                        units_by_post_for_sale[unit.post_for_saleID].append(unit)
                    print("post_invoice")
                    first_unit = buyer_units_posted_for_sale.first()
                    if first_unit:
                        post_invoice = first_unit.unitID.invoice
                        print("post_invoice:", post_invoice)

                        # Iterate through each group
                        for post_for_saleID, units in units_by_post_for_sale.items():
                            if units:
                                # Fetch the post_for_sale object to access its fields
                                post_for_sale = models.Post_for_sale.objects.get(id=post_for_saleID.id)
                                invoice_data = {
                                    'id': post_invoice.id,
                                    'Invoice_id': post_invoice.invoice_id,
                                    'Invoice_primary_id': post_invoice.primary_invoice_id,
                                    'Buyer_id': buyer.id,
                                    'Buyer_user_id': buyer.user_id.id,
                                    'post_for_saleID': post_for_saleID.id,
                                    'Posted_no_of_units': post_for_sale.no_of_units,
                                    'Posted_remaining_units': post_for_sale.remaining_units,
                                    'Posted_per_unit_price': post_for_sale.per_unit_price,
                                    'Posted_total_price': post_for_sale.total_price,
                                    'Posted_from_date': post_for_sale.from_date,
                                    'Posted_to_date': post_for_sale.to_date,
                                    'Invoice_name': post_invoice.product_name,
                                    'Buyer_Purchased_date': buyer.purchase_date,
                                    'Buyer_Purchased_time': buyer.purchase_time,
                                    'Invoice_interest': post_invoice.interest,
                                    'Invoice_xirr': post_invoice.xirr,
                                    'Invoice_irr': post_invoice.irr,
                                    'Invoice_tenure_in_days': post_invoice.tenure_in_days,
                                    'Invoice_expiration_time': post_invoice.expiration_time,
                                    'isAdmin': buyer.user_id.user.is_admin,
                                    'type': 'PostedForSale'
                                }
                                invoice_data_list.append(invoice_data)
                else :
                    print("dnkesbnzfvk")
                    pass
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
                return JsonResponse({"message": "User not found"}, status=400)

            try:
                # bankAcc = models.BankAccountDetails.objects.get(user_role=user_role)
                buyer_wallet = models.Wallet.objects.get(user_role=user_role)
                print("buyer_wallet ,",buyer_wallet.primary_bankID)
            except models.Wallet.DoesNotExist:
                return JsonResponse({"message": "Buyer Wallet not found"}, status=400)
            
            try:
                postForSale = models.Post_for_sale.objects.get(id=postForSaleID)
            except models.Post_for_sale.DoesNotExist:
                return JsonResponse({"message": "postForSaleID not found"}, status=400)
            
            print("postForSale.remaining_units : ",postForSale.remaining_units)
            
            if postForSale.remaining_units < no_of_units:
                return JsonResponse({"message": "Not enough units available for sale"}, status=400)
            
            if postForSale.remaining_units == no_of_units :
                print("jvdcsvcjs")
                pass

            print("assffghjk")
            total_price = postForSale.per_unit_price * no_of_units

            if buyer_wallet.OutstandingBalance < total_price:
                return JsonResponse({"message": "Insufficient balance in buyer's wallet"}, status=400)
            print("buyer_wallet.OutstandingBalance : ",buyer_wallet.OutstandingBalance)
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
                
                print("debxjk")
                units_for_sale = models.Post_For_Sale_UnitTracker.objects.filter(
                    post_for_saleID=postForSale,
                    sellersID__isnull=True
                ).order_by('id')[:no_of_units]

                print("units_for_sale.count() :",units_for_sale.count())

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
                    unit.unitID.current_owner = user_role
                    unit.unitID.save()

                    print("ksjcbd b")
                    salespurchaseReport = models.SalePurchaseReport.objects.create(
                        invoiceID = postForSale.invoice_id ,
                        unitID = unit.unitID ,
                        seller_ID = postForSale.user_id,
                        buyerID_ID = user_role ,
                        Sale_Buy_Date = timezone.now().date(),
                        Sale_Buy_per_unit_price = postForSale.per_unit_price,
                        ListingDate = timezone.now().date(),
                        no_of_days_units_held = (sales.sell_date - postForSale.post_date).days,
                        interest_due_to_seller = ( postForSale.per_unit_price * 10 ) / 100,
                        TDS_deducted = ( postForSale.per_unit_price * 10 ) / 100,
                        IRR = postForSale.invoice_id.irr
                    )
                print("dbjcksb")
                
                buyer_wallet.OutstandingBalance -= total_price
                buyer_wallet.save()
                print("bkdsbcbs")
                try :
                    seller_wallet = models.Wallet.objects.get(user_role=postForSale.user_id)
                    print("seller_wallet ,",seller_wallet.primary_bankID)
                except models.Wallet.DoesNotExist :
                    return JsonResponse({"message": "Seller wallet is not made"},status = 500)
                seller_wallet.OutstandingBalance += total_price
                seller_wallet.save()

                models.WalletTransaction.objects.create(
                    wallet = buyer_wallet ,
                    type = "buy" ,
                    debitedAmount = total_price ,
                    status = 'response' ,
                    source = 'wallet_to_buy',
                    from_wallet = buyer_wallet,
                    to_wallet = seller_wallet,
                    invoice = postForSale.invoice_id ,
                    time_date = timezone.now()
                )

                # seller
                models.WalletTransaction.objects.create(
                    wallet = seller_wallet ,
                    type = "sell" ,
                    creditedAmount = total_price ,
                    status = 'response' ,
                    source = 'sell_to_wallet',
                    from_wallet = buyer_wallet ,
                    to_wallet = seller_wallet,
                    invoice = postForSale.invoice_id,
                    time_date = timezone.now()
                )

                postForSale.remaining_units -= no_of_units
                postForSale.save()

                if postForSale.remaining_units == 0:
                    postForSale.sold= True

            return JsonResponse({"message": "Units bought successfully", "buyer_id": buyer.id,"user" : user_role.id , "salespurchaseReport":salespurchaseReport.id}, status=201)        
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
            total_price = data.get('total_price')
            from_date = data.get('from_date')
            to_date = data.get('to_date')

            if not all([userRoleID, no_of_units, per_unit_price]):
                return JsonResponse({"message": "All fields are required"}, status=400)

            try:
                user_role = models.UserRole.objects.get(id=userRoleID)
            except models.UserRole.DoesNotExist:
                return JsonResponse({"message": "User role not found"}, status=400)

            try:
                buyer = models.Buyers.objects.get(id=buyerID)
            except models.Buyers.DoesNotExist:
                return JsonResponse({"message": "Buyer not found"}, status=400)

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
                    total_price = total_price,
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
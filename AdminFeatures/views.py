from datetime import datetime
from django.utils import timezone
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from UserFeatures import models
from django.utils import timezone
from django.db import transaction

@csrf_exempt
def AdminLoginAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mobile = data.get('mobile')
            password = data.get('password')

            if not mobile or not password:
                return JsonResponse({"message": "mobile and password are required"}, status=400)

            try:
                user = models.User.objects.get(mobile=mobile)
                if user.check_password(password):
                    if user.is_admin:
                        return JsonResponse({"message": "Admin logged in successfully", "id": user.id}, status=200)
                    else:
                        return JsonResponse({"message": "User is not an admin"}, status=403)
                else:
                    return JsonResponse({"message": "Invalid credentials"}, status=401)
            except models.User.DoesNotExist:
                return JsonResponse({"message": "Invalid credentials"}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Only POST method is allowed"}, status=405)

@csrf_exempt
def InvoicesAPI(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')

            if not user_id:
                return JsonResponse({"message": "user_id is required"}, status=400)

            try:
                user = models.User.objects.get(id=user_id)
            except models.User.DoesNotExist:
                return JsonResponse({"message": "User not found"}, status=404)

            if not user.is_admin:
                return JsonResponse({"message": "For this operation you have to register yourself with admin role"}, status=403)
            
            primary_invoice_id = data.get('primary_invoice_id')
            no_of_fractional_units = data.get('no_of_fractional_Unit')
            name = data.get('name')
            post_date = timezone.now().date()
            post_time = timezone.now().time()
            interest_rate = data.get('interest_rate')
            print(interest_rate)
            xirr = data.get('xirr')
            tenure_in_days = data.get('tenure_in_days')
            principle_amt = data.get('principle_amt')
            expiration_time = data.get('expiration_time')

            if not all([primary_invoice_id, no_of_fractional_units , name, interest_rate, xirr, tenure_in_days, principle_amt, expiration_time]):
                return JsonResponse({"message": "All fields are required"}, status=400)
            
            print("before create")
            invoice = models.Invoices.objects.create(
                primary_invoice_id=primary_invoice_id,
                no_of_partitions=no_of_fractional_units,
                name=name,
                post_date=post_date,
                post_time=post_time,
                interest=interest_rate,
                xirr=xirr,
                tenure_in_days=tenure_in_days,
                principle_amt=principle_amt,
                expiration_time=expiration_time,
                remaining_partitions = no_of_fractional_units ,
                sold = False
            )
            print("after create")

            fractional_units = [
                models.FractionalUnits(invoice=invoice)
                for _ in range(no_of_fractional_units)
            ]
            models.FractionalUnits.objects.bulk_create(fractional_units)

            return JsonResponse({"message": "Invoice created successfully", "invoice_id": invoice.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    else:
        return JsonResponse({"message": "Only POST methods are allowed"}, status=405)
    
@csrf_exempt
def SalesPurchasedReportAPI(request,User_id):
    if request.method == 'GET':
        try:
            # data = json.loads(request.body)
            # User_id = data.get('user_id')

            if not User_id:
                return JsonResponse({"message": "User_id is required"}, status=400)
            
            try:
                user = models.User.objects.get(id=User_id)
            except models.User.DoesNotExist:
                return JsonResponse({"message": "User not found"}, status=404)

            if not user.is_admin:
                return JsonResponse({"message": "For this operation you have to register yourself with admin role"}, status=403)
            
            with transaction.atomic():
                try:
                    sales_purchase_reports = models.SalePurchaseReport.objects.all()
                    report_list = []
                    for report in sales_purchase_reports:

                        try:
                            pan_card_no = models.PanCardNos.objects.get(user_role=report.buyer.user).pan_card_no
                            seller_pan_card_no = models.PanCardNos.objects.get(user_role = report.seller.user).pan_card_no
                        except models.PanCardNos.DoesNotExist:
                            pan_card_no = None
                            seller_pan_card_no = None

                        # purchase_datetimet = datetime.combine(report.buyer.purchase_date, report.buyer.purchase_time)
                        # purchase_datetime = timezone.make_aware(purchase_datetimet, timezone.get_default_timezone())
                        # print(purchase_datetime)
                        # print(timezone.now())
                        # print(report.buyer.purchase_date, "  ",report.buyer.purchase_time)
                        try:
                            credited_transaction = models.OutstandingBalanceTransaction.objects.get(
                                wallet = report.seller.wallet,
                                time_date="2024-07-02 18:16:09.123273+00"
                            )
                            print(credited_transaction)
                            credited_amount = credited_transaction.creditedAmount
                        except models.OutstandingBalanceTransaction.DoesNotExist:
                            credited_amount = None

                        seller_info = {}
                        if report.seller.User.role == 'individual':
                            individual_details = models.IndividualDetails.objects.get(user_role=report.seller.User)
                            seller_info = {
                                'first_name': individual_details.first_name,
                                'last_name': individual_details.last_name,
                            }
                        elif report.seller.User.role == 'company':
                            company_details = models.CompanyDetails.objects.get(user_role=report.seller.User)
                            seller_info = {
                                'company_name': company_details.company_name,
                            }

                        report_data = {
                            'id': report.id,
                            'purchaser_Info' :{
                                'purchaser_id' : report.buyer.id,
                                'purchased_units' : report.buyer.no_of_partitions,
                                'purchased_Date' : report.buyer.purchase_date,
                                'purchaser_pan_card_no': pan_card_no,
                                'purchaser_name' : {
                                    'user' : report.buyer.user.user.mobile
                                }
                             },
                            'seller_info': {
                                "Value_of_Per_Unit" : ( report.seller.amount ) / (report.seller.no_of_partitions),
                                'sell_Date' : report.seller.sell_date,
                                'Name_of_Co.': seller_info,
                                'Pan_Card_No' : seller_pan_card_no,
                                'total_amt_credited': credited_amount, #error
                            },
                        }
                        report_list.append(report_data)

                    return JsonResponse({"sales_purchase_reports": report_list}, status=200)

                except models.SalePurchaseReport.DoesNotExist:
                    return JsonResponse({"message": "SalePurchaseReport not found"}, status=404)
                # return JsonResponse({"sales_purchase_report" : sales_purchase_report},status=200)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    else:
        return JsonResponse({"message": "Only POST methods are allowed"}, status=405)
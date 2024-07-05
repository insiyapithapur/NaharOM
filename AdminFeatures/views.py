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
                        report_data = {
                            'id': report.id,
                            'seller': {
                                "mobile" : report.seller.id,
                            },
                            'buyer': report.buyer.id,
                            'invoice': {
                                "id" : report.unit.invoice.name,
                            },
                            # 'amount': report.amount,
                            'no_of_partitions': report.unit.current_owner,
                            # 'sell_date': report.sell_date,
                            # 'sell_time': report.sell_time,
                            # 'purchase_date': report.purchase_date,
                            'transaction_date': report.transaction_date,
                            # Add any other fields as required
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
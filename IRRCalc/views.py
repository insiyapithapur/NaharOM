import datetime
from django.shortcuts import render
from django.http import JsonResponse
from .fixed_price import calculate_buyer_price
import json 

@csrf_exempt
def FixedPriceIRRAPI(request):
    if request.method == "POST":
        try:
            # "BUYER" or "SELLER"
            type = request.GET.get("type", "").upper()
            loan_amount = float(request.GET.get("loan_amount", 0)) #from invoice table (principle amt from primary)  
            num_fractions = int(request.GET.get("num_fractions", 0)) # from invoice table
            annual_interest_rate = float(request.GET.get("annual_interest_rate", 0)) / 100 #from invoice table (interest_rate_fixed)
            loan_period_years = int(request.GET.get("loan_period_years", 0)) #invoice table (tenure_in_days)
            units_bought = int(request.GET.get("units_bought", 0))
            disbursed_date = datetime.strptime(request.GET.get("disbursed_date", ""), "%Y-%m-%d").date()#invoice table
            first_payment_date = datetime.strptime(request.GET.get("first_payment_date", ""), "%Y-%m-%d").date()
            payment_frequency = request.GET.get("payment_frequency", "MONTHLY").upper()
            
            if type == "BUYER":
                xirr_value = calculate_buyer_price(
                    loan_amount, num_fractions, annual_interest_rate, loan_period_years, 
                    units_bought, disbursed_date, first_payment_date, payment_frequency
                )
                return JsonResponse({"XIRR": f"{xirr_value * 100:.2f}%"},status=200)
            elif type == "SELLER":
                return JsonResponse({"XIRR": "seller"},status=200)
            else :
                return JsonResponse({"message": "type is invalid"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else :
        return JsonResponse({"message": "Only POST methods is allowed"}, status=405)
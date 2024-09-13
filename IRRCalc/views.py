import datetime
from django.shortcuts import render
from django.http import JsonResponse
from .fixed_price import calculate_buyer_price , Calculate_Seller_price , calculate_cashflow_with_flexible_xirr
import json 
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def FixedPriceIRRAPI(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            type = data.get("type", "").upper()
            loan_amount = data.get("loan_amount") #from invoice table (principle amt from primary)  
            num_fractions = data.get("num_fractions")# from invoice table
            annual_interest_rate = data.get("annual_interest_rate") #from invoice table (interest_rate_fixed)
            loan_period_years = data.get("loan_period_years") #invoice table (tenure_in_days)
            units_bought = data.get("units_bought")
            disbursed_date = datetime.date(2024, 4, 1)
            first_payment_date = datetime.date(2024, 5, 1)
            payment_frequency = data.get('payment_frequency')
            
            if type == "BUYER":
                dates, amounts, xirr_value = calculate_buyer_price(
                    loan_amount, num_fractions, annual_interest_rate, loan_period_years, 
                    units_bought, disbursed_date, first_payment_date, payment_frequency
                )
                payments = [
                    {
                        "payment_number": i,
                        "date": dates[i].strftime("%Y-%m-%d"),
                        "amount": f"{amounts[i]:.2f}"
                    }
                    for i in range(1, len(dates))
                ]

                response_data = {
                    "XIRR": f"{xirr_value * 100:.2f}%",
                    "investment_amount": f"{abs(amounts[0]):.2f}",
                    "payments": payments
                }

                return JsonResponse(response_data, status=200)
            elif type == "SELLER":
                target_xirr = data.get("target_xirr")
                additional_payment = data.get("additional_payment")
                end_date = datetime.date(2024, 8, 18)
                fractional_unit_value = loan_amount / num_fractions
                if target_xirr :
                    investment_amount = fractional_unit_value * units_bought
                    end_date = datetime.date(2024, 8, 18)
                    result = calculate_cashflow_with_flexible_xirr(
                        fractional_unit_value,
                        loan_amount,
                        num_fractions,
                        annual_interest_rate,
                        units_bought,
                        loan_period_years,
                        disbursed_date,
                        first_payment_date,
                        payment_frequency,
                        end_date,
                        target_xirr
                    )
                    response_data = {
                        "verified_target_xirr": result["verified_target_xirr"],
                        "difference_from_target": result["difference_from_target"],
                        "cashflow_details": result["cashflow_details"],
                        "sale_price": result["sale_price"]
                    }

                    return JsonResponse(response_data, status=200)
                # Case: Buying 3 units
                units_bought = 3
                dates, amounts, xirr_value = Calculate_Seller_price(
                    fractional_unit_value,
                    loan_amount,
                    num_fractions,
                    annual_interest_rate,
                    units_bought,
                    loan_period_years,
                    disbursed_date,
                    first_payment_date,
                    payment_frequency,
                    additional_payment,
                    end_date
                )
                payments = [
                    {
                        "detail": f"{'Investment' if i == 0 else f'Payment {i}'} on {date.strftime('%Y-%m-%d')}: {amount:.2f}"
                    }
                    for i, (date, amount) in enumerate(zip(dates, amounts))
                ]
                response_data = {
                    "investment_amount": f"{abs(amounts[0]):.2f}",
                    "payments": payments,
                    "XIRR_with_additional_payment": f"{xirr_value * 100:.2f}%"
                }
                return JsonResponse(response_data, status=200)
            else :
                return JsonResponse({"message": "type is invalid"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else :
        return JsonResponse({"message": "Only POST methods is allowed"}, status=405)
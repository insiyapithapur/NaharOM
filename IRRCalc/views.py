import datetime
from django.shortcuts import render
from django.http import JsonResponse
from .fixed_price import calculate_buyer_price , Calculate_Seller_price , calculate_cashflow_with_flexible_xirr
from .Declining_Principal import Declining_calculate_Buyerprice_to_XIRR , Declining_calculate_Sellerprice_to_XIRR , Declining_calculate_SellerXIRR_to_price
from .Balloon_payment import Balloon_calculate_Buyerprice_to_XIRR , Balloon_calculate_Sellerprice_to_XIRR , Balloon_calculate_SellerXIRR_to_price
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
    

@csrf_exempt
def DecliningPrincipalAPI(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            type = data.get("type").upper()
            loan_amount = data.get("loan_amount")
            num_fractions = data.get("num_fractions")
            fractional_unit_value = loan_amount / num_fractions
            annual_interest_rate = data.get("annual_interest_rate")
            total_installments = data.get("total_installments")
            loan_period_years = data.get("loan_period_years")
            units_bought = data.get("units_bought")
            payment_frequency = data.get("payment_frequency").upper()
            monthly_payment = data.get("monthly_payment")
            disbursed_date = datetime.date(2024, 4, 1)
            first_payment_date = datetime.date(2024, 5, 1)
            additional_payment = data.get("additional_payment")
            end_date = datetime.date(2024, 8, 18)

            if type == "BUYER":
                dates, amounts, xirr_value = Declining_calculate_Buyerprice_to_XIRR(
                    fractional_unit_value,
                    loan_amount,
                    num_fractions,
                    annual_interest_rate,
                    total_installments,
                    units_bought,
                    loan_period_years,
                    disbursed_date,
                    first_payment_date,
                    payment_frequency,
                    monthly_payment
                )
                response_data = {
                    "investment_amount": f"{abs(amounts[0]):.2f}",
                    "payments": [
                        {"payment_number": i, "date": dates[i].strftime('%Y-%m-%d'), "amount": f"{amounts[i]:.2f}"}
                        for i in range(1, len(dates))
                    ],
                    "xirr": f"{xirr_value * 100:.2f}%"
                }

                return JsonResponse(response_data, status=200)
            elif type == "SELLER":
                target_xirr = data.get("target_xirr")
                if target_xirr :
                    dates, amounts, additional_amount, final_xirr, difference = Declining_calculate_SellerXIRR_to_price(
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
                        target_xirr,
                        monthly_payment
                    )
                    
                    cashflow_details = [{"date": date.strftime('%Y-%m-%d'), "amount": f"{amount:.2f}"} for date, amount in zip(dates, amounts)]
                    response_data = {
                        "verified_target_xirr": f"{final_xirr:.8%}",
                        "difference_from_target": f"{abs(difference):.10f}",
                        "cashflow_details": cashflow_details,
                        "sale_price": f"{additional_amount:.2f}",
                    }

                    return JsonResponse(response_data, status=200)
                dates, amounts, xirr_value = Declining_calculate_Sellerprice_to_XIRR(
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
                    end_date,
                    monthly_payment
                )

                response_data = {
                    "investment_amount": f"{abs(amounts[0]):.2f}",
                    "payments": [
                        {"payment_number": i, "date": date.strftime('%Y-%m-%d'), "amount": f"{amount:.2f}"}
                        if i > 0 else {"investment": date.strftime('%Y-%m-%d'), "amount": f"{amount:.2f}"}
                        for i, (date, amount) in enumerate(zip(dates, amounts), 0)
                    ],
                    "xirr": f"{xirr_value:.2%}"
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
    
@csrf_exempt
def BalloonPaymentAPI(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            type = data.get("type").upper()
            loan_amount = data.get("loan_amount")
            num_fractions = data.get("num_fractions")
            fractional_unit_value = loan_amount / num_fractions
            print("fractional_unit_value ",fractional_unit_value)
            annual_interest_rate = data.get("annual_interest_rate")
            total_installments = data.get("total_installments")
            loan_period_years = data.get("loan_period_years")
            units_bought = data.get("units_bought")
            payment_frequency = data.get("payment_frequency").upper()
            disbursed_date = datetime.date(2024, 4, 1)
            first_payment_date = datetime.date(2024, 5, 1)
            additional_payment = data.get("additional_payment")
            end_date = datetime.date(2024, 8, 18)
            investment_amount = data.get("investment_amount")

            if type == "BUYER":
                dates, amounts, xirr_value = Balloon_calculate_Buyerprice_to_XIRR(
                    fractional_unit_value,
                    loan_amount,
                    num_fractions,
                    annual_interest_rate,
                    total_installments,
                    units_bought,
                    loan_period_years,
                    disbursed_date,
                    first_payment_date,
                    payment_frequency,
                    investment_amount
                )
                payments = [{"payment_number": i, "date": dates[i].strftime('%Y-%m-%d'), "amount": f"{amounts[i]:.2f}"}
                for i in range(1, len(dates))]
                response_data = {
                    "investment_amount": f"{abs(amounts[0]):.2f}",
                    "payments": payments,
                    "xirr": f"{xirr_value * 100:.2f}%"  # XIRR as a percentage
                }

                return JsonResponse(response_data, status=200)
            elif type == "SELLER":
                Seller_monthly_payment= data.get("monthly_payment") * units_bought
                target_xirr = data.get("target_xirr")
                if target_xirr :
                    dates, amounts, final_xirr, additional_amount = Balloon_calculate_SellerXIRR_to_price(
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
                        target_xirr,
                        Seller_monthly_payment
                    )
                    cashflow_details = [
                        {"date": date.strftime('%Y-%m-%d'), "amount": f"{amount:.2f}"}
                        for date, amount in zip(dates, amounts)
                    ]

                    # Prepare the final response
                    response_data = {
                        "verified_target_xirr": f"{final_xirr:.8%}",
                        "difference_from_target": f"{abs(final_xirr - target_xirr):.10f}",
                        "cashflow_details": cashflow_details,
                        "sale_price": f"{additional_amount:.2f}",
                        "final_cashflow": {
                            "date": dates[-1].strftime('%Y-%m-%d'),
                            "sale_price": f"{additional_amount:.2f}"
                        }
                    }

                    return JsonResponse(response_data, status=200)
                selling_price = data.get("selling_price")
                dates, amounts, xirr_value = Balloon_calculate_Sellerprice_to_XIRR(
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
                    end_date,
                    Seller_monthly_payment,
                    selling_price
                )
                payments = [
                    {"payment_number": i, "date": date.strftime('%Y-%m-%d'), "amount": f"{amount:.2f}"}
                    if i > 0 else {"investment": date.strftime('%Y-%m-%d'), "amount": f"{abs(amount):.2f}"}
                    for i, (date, amount) in enumerate(zip(dates, amounts), 0)
                ]

                response_data = {
                    "investment_amount": f"{abs(amounts[0]):.2f}",
                    "payments": payments,
                    "xirr": f"{xirr_value:.2%}"
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
import datetime
import pyxirr
from dateutil.relativedelta import relativedelta

def days_between_dates(date1, date2):
    return (date2 - date1).days

def get_next_schedule_date(date, payment_frequency):
    if payment_frequency == "MONTHLY":
        return (date + relativedelta(months=1)).replace(day=1)
    elif payment_frequency == "QUARTERLY":
        return (date + relativedelta(months=3)).replace(day=1)
    elif payment_frequency == "HALF_YEARLY":
        return (date + relativedelta(months=6)).replace(day=1)
    elif payment_frequency == "YEARLY":
        return (date + relativedelta(years=1)).replace(day=1)
    else:
        raise ValueError("Unsupported payment frequency")

def calculate_buyer_price(loan_amount, num_fractions, annual_interest_rate, loan_period_years, units_bought, disbursed_date, first_payment_date, payment_frequency):
    # Buyer price calculation logic (simplified)
    fractional_unit_value = loan_amount / num_fractions
    total_installments = loan_period_years * 12
    principal_per_installment = loan_amount / total_installments
    daily_interest_rate = (1 + annual_interest_rate) ** (1 / 365) - 1

    investment_amount = fractional_unit_value * units_bought
    dates = [disbursed_date]
    amounts = [-investment_amount]

    remaining_principal = investment_amount
    current_date = first_payment_date
    prev_date = disbursed_date

    while remaining_principal > 0:
        days_between = days_between_dates(prev_date, current_date)
        interest_payment = daily_interest_rate * days_between * remaining_principal
        principal_payment = (principal_per_installment / num_fractions) * units_bought

        if principal_payment > remaining_principal:
            principal_payment = remaining_principal

        total_payment = principal_payment + interest_payment
        dates.append(current_date)
        amounts.append(total_payment)

        remaining_principal -= principal_payment
        prev_date = current_date
        current_date = get_next_schedule_date(current_date, payment_frequency)

    xirr_value = pyxirr.xirr(dates, amounts)
    return xirr_value
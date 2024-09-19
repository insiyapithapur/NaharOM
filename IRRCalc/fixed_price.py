import numpy as np
import datetime
import pyxirr
from scipy import optimize
from dateutil.relativedelta import relativedelta

def days_between_dates(date1, date2):
    return (date2 - date1).days

def get_next_schedule_date(date, payment_frequency):
    if payment_frequency == "MONTHLY":
        # Move to the next month and set to the first day of that month
        return (date + relativedelta(months=1)).replace(day=1)
    elif payment_frequency == "QUARTERLY":
        # Move to the next quarter and set to the first day of that quarter
        return (date + relativedelta(months=3)).replace(day=1)
    elif payment_frequency == "HALF_YEARLY":
        # Move to the next half-year and set to the first day of that month
        return (date + relativedelta(months=6)).replace(day=1)
    elif payment_frequency == "YEARLY":
        # Move to the next year and set to the first day of that month
        return (date + relativedelta(years=1)).replace(day=1)
    else:
        raise ValueError("Unsupported payment frequency")
    
def frequency_interest(interest_rate, days):
    return (1 + interest_rate) ** (1 / days) - 1

def calculate_Fixedbuyer_price_to_XIRR(
    fractional_unit_value,
    loan_amount, # principle amount of the loan eg :- 10,000,000
    num_fractions, # no of fraction for the loan eg :- 20 
    annual_interest_rate, # interest rate that buyer has to pay with invested amount
    total_installments, #The total duration of the loan in years.
    units_bought, 
    loan_period_years,
    disbursed_date, #The start date of the loan 
    first_payment_date, #date when the buyer makes their first installment payment.
    payment_frequency #typically set by the borrower (or lender)
):
    
    # total_installments = loan_period_years * 12 #months
    principal_per_installment = loan_amount / total_installments
    daily_interest_rate = frequency_interest(annual_interest_rate, 365)
    
    investment_amount = fractional_unit_value * units_bought

    dates = []
    amounts = []

    remaining_principal = investment_amount

    # Initial investment outflow
    dates.append(disbursed_date)
    amounts.append(-investment_amount)

    current_date = first_payment_date
    prev_date = disbursed_date

    while remaining_principal > 0:
        days_between = days_between_dates(prev_date, current_date)
        interest_payment = daily_interest_rate * days_between * remaining_principal #investment amount
        principal_payment = (principal_per_installment / num_fractions) * units_bought #total loan amount 

        if principal_payment > remaining_principal:
            principal_payment = remaining_principal

        total_payment = principal_payment + interest_payment

        
        dates.append(current_date)
        amounts.append(total_payment)

        remaining_principal -= principal_payment
        print(f"principal_payment: {principal_payment:.2f}, interest_payment: {interest_payment:.2f}, total_payment: {total_payment:.2f}, remaining_principal: {remaining_principal:.2f}, prev_date: {prev_date}, current_date: {current_date}")

        prev_date = current_date
        current_date = get_next_schedule_date(current_date, payment_frequency)
        
       
    # Calculate XIRR using pyxirr
    xirr_value = pyxirr.xirr(dates, amounts)
    return dates, amounts, xirr_value


def calculate_FixedSeller_price_to_XIRR(
    fractional_unit_value,
    loan_amount, # principal amount of the loan, e.g. 10,000,000
    num_fractions, # number of fractions for the loan, e.g. 20 
    annual_interest_rate, # interest rate that buyer has to pay with invested amount
    units_bought, 
    loan_period_years,
    disbursed_date, # start date of the loan 
    first_payment_date, # date when the buyer makes their first installment payment
    payment_frequency, # typically set by the borrower (or lender)
    additional_payment, # the extra amount to be added to the last installment
    end_date # Flexible end date (can be partial month)
):
    total_installments = loan_period_years * 12 # Full months
    principal_per_installment = loan_amount / total_installments
    daily_interest_rate = 0.0004996359

    
    # Scale investment amount by units bought
    investment_amount = fractional_unit_value * units_bought

    dates = []
    amounts = []

    remaining_principal = investment_amount

    # Initial investment outflow
    dates.append(disbursed_date)
    amounts.append(-investment_amount)  # Outflow (negative)
    
    current_date = first_payment_date
    prev_date = disbursed_date
    installment_count = 0

    # Calculate until last full installment month
    while current_date < end_date:
        # Increment installment count
        installment_count += 1
        
        # Calculate the number of days between payments
        days_between = (current_date - prev_date).days

        # Interest payment is scaled by the units bought
        interest_payment = daily_interest_rate * days_between * remaining_principal
        # Principal payment is scaled by the units bought
        principal_payment = (principal_per_installment / num_fractions) * units_bought

        if principal_payment > remaining_principal:
            principal_payment = remaining_principal

        # Normal total payment for all months except the last
        total_payment = principal_payment + interest_payment
        
        # Append the current payment date and amount
        dates.append(current_date)
        amounts.append(total_payment)

      
        # Subtract the principal payment from the remaining principal
        remaining_principal -= principal_payment
        print(f"principal_payment: {principal_payment:.2f}, interest_payment: {interest_payment:.2f}, total_payment: {total_payment:.2f}, remaining_principal: {remaining_principal:.2f}, prev_date: {prev_date}, current_date: {current_date}")


        # Move to the next payment date
        prev_date = current_date
        current_date = get_next_schedule_date(current_date, payment_frequency)

    # Now handle the partial month (if there is a partial month)
    if current_date != end_date:
        # Calculate the remaining days from the last full installment to the flexible end date
        partial_days = (end_date - prev_date).days
        
        # Calculate interest for the partial month
        partial_interest_payment = daily_interest_rate * partial_days * remaining_principal
        
        # Calculate the proportional principal for the partial period
        # Formula: (Partial Days / Full Month Days) * Principal per Installment
        full_month_days = (get_next_schedule_date(prev_date, payment_frequency) - prev_date).days
        partial_principal_payment = (partial_days / full_month_days) * principal_payment
        
        if partial_principal_payment > remaining_principal:
            partial_principal_payment = remaining_principal

        # Add additional payment to the last installment if applicable
        total_payment = partial_principal_payment + partial_interest_payment + additional_payment

        # Append the final payment date and amount
        dates.append(end_date)
        amounts.append(total_payment)

        # Debugging output
        print(f"Last installment: partial_principal_payment: {partial_principal_payment:.2f}, "
              f"partial_interest_payment: {partial_interest_payment:.2f}, "
              f"total_payment: {total_payment:.2f}, remaining_principal: {remaining_principal:.2f}, "
              f"prev_date: {prev_date}, end_date: {end_date} ",
              f"full_month_days: {full_month_days}" 
              )

    # Calculate XIRR based on cash flows (dates and amounts)
    xirr_value = pyxirr.xirr(dates, amounts)
    return dates, amounts, xirr_value


def calculate_xirr(cashflows, dates, additional_amount):
    # Add the additional amount to the last cashflow
    cashflows[-1] += additional_amount
    return pyxirr.xirr(dates, cashflows)

def find_additional_amount(target_xirr, cashflows, dates):
    def objective_function(additional_amount):
        return calculate_xirr(cashflows.copy(), dates, additional_amount) - target_xirr

    # Use Brent's method to find the root (where calculated target_xirr equals target target_xirr)
    result = optimize.brentq(objective_function, 0, 10 * abs(cashflows[0]))
    return result

def calculate_FixedSeller_XIRR_to_price(
    fractional_unit_value,
    loan_amount, # principal amount of the loan, e.g. 10,000,000
    num_fractions, # number of fractions for the loan, e.g. 20 
    annual_interest_rate, # interest rate that buyer has to pay with invested amount
    units_bought, 
    loan_period_years,
    disbursed_date, # start date of the loan 
    first_payment_date, # date when the buyer makes their first installment payment
    payment_frequency, # typically set by the borrower (or lender)
    end_date, # Flexible end date (can be partial month)
    target_xirr
):
    total_installments = loan_period_years * 12 # Full months
    principal_per_installment = loan_amount / total_installments
    daily_interest_rate = 0.0004996359

    investment_amount = fractional_unit_value * units_bought
    dates = []
    amounts = []

    remaining_principal = investment_amount

    dates.append(disbursed_date)
    amounts.append(-investment_amount)  # Outflow (negative)

    current_date = first_payment_date
    prev_date = disbursed_date
    installment_count = 0

    while current_date < end_date: 
        installment_count += 1

        days_between = (current_date - prev_date).days
        
        # Interest payment is scaled by the units bought
        interest_payment = daily_interest_rate * days_between * remaining_principal
        # Principal payment is scaled by the units bought
        principal_payment = (principal_per_installment / num_fractions) * units_bought

        if principal_payment > remaining_principal:
            principal_payment = remaining_principal

        # Normal total payment for all months except the last
        total_payment = principal_payment + interest_payment
        
        # Append the current payment date and amount
        dates.append(current_date)
        amounts.append(total_payment)

        # Subtract the principal payment from the remaining principal
        remaining_principal -= principal_payment
        print(f"principal_payment: {principal_payment:.2f}, interest_payment: {interest_payment:.2f}, total_payment: {total_payment:.2f}, remaining_principal: {remaining_principal:.2f}, prev_date: {prev_date}, current_date: {current_date}")


        # Move to the next payment date
        prev_date = current_date
        current_date = get_next_schedule_date(current_date, payment_frequency)

    if current_date != end_date:
        # Calculate the remaining days from the last full installment to the flexible end date
        partial_days = (end_date - prev_date).days
        
        # Calculate interest for the partial month
        partial_interest_payment = daily_interest_rate * partial_days * remaining_principal
        
        # Calculate the proportional principal for the partial period
        # Formula: (Partial Days / Full Month Days) * Principal per Installment
        full_month_days = (get_next_schedule_date(prev_date, payment_frequency) - prev_date).days
        partial_principal_payment = (partial_days / full_month_days) * principal_payment
        
        if partial_principal_payment > remaining_principal:
            partial_principal_payment = remaining_principal

        # Add additional payment to the last installment if applicable
        total_payment = partial_principal_payment + partial_interest_payment 

        # Append the final payment date and amount
        dates.append(end_date)
        amounts.append(total_payment)

    # Find the additional amount needed to achieve the target target_xirr
    additional_amount = find_additional_amount(target_xirr, amounts, dates)

    print(f"Additional amount (sell price) needed to achieve {target_xirr:.2%} target_xirr: {additional_amount:.2f}")

    # Verify the result
    final_xirr = calculate_xirr(amounts, dates, additional_amount)
    print(f"Verified target_xirr: {final_xirr:.8%}")
    print(f"Difference from target: {abs(final_xirr - target_xirr):.10f}")

    print("\nCashflow details:")
    for date, amount in zip(dates, amounts):
        print(f"{date}: {amount:.2f}")
    print(f"{dates[-1]}: Sale Price: {additional_amount:.2f}")

    cashflow_details = [
        {"date": date.strftime('%Y-%m-%d'), "amount": f"{amount:.2f}"}
        for date, amount in zip(dates, amounts)
    ]

    result = {
        "verified_target_xirr": f"{final_xirr:.8%}",
        "difference_from_target": f"{abs(final_xirr - target_xirr):.10f}",
        "cashflow_details": cashflow_details,
        "sale_price": f"{additional_amount:.2f}"
    }

    return result
def compute_emi(principal, annual_rate, tenure_months):
    """EMI = P * r * (1+r)^n / ((1+r)^n - 1)"""
    if annual_rate == 0 or tenure_months == 0:
        return 0.0
    r = annual_rate / 12 / 100
    n = tenure_months
    if r == 0:
        return principal / n
    emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return round(emi, 2)


def compute_total_interest(principal, annual_rate, tenure_months):
    """Total interest payable over the loan tenure."""
    emi = compute_emi(principal, annual_rate, tenure_months)
    total_payable = emi * tenure_months
    total_interest = total_payable - principal
    return round(max(total_interest, 0), 2)


def compute_sip_maturity(monthly, annual_return_pct, years):
    """SIP maturity calculator with month-by-month breakdown."""
    if monthly <= 0 or years <= 0:
        return {"total_invested": 0, "estimated_returns": 0, "maturity_value": 0, "multiplier": 0, "yearly_data": []}
    r = annual_return_pct / 12 / 100
    n_months = years * 12
    yearly_data = []
    corpus = 0
    for month in range(1, n_months + 1):
        corpus = (corpus + monthly) * (1 + r)
        if month % 12 == 0:
            total_invested = monthly * month
            yearly_data.append({
                "year": month // 12,
                "invested": round(total_invested, 2),
                "corpus": round(corpus, 2)
            })
    total_invested = monthly * n_months
    maturity_value = round(corpus, 2)
    estimated_returns = round(maturity_value - total_invested, 2)
    multiplier = round(maturity_value / total_invested, 2) if total_invested > 0 else 0
    return {
        "total_invested": total_invested,
        "estimated_returns": estimated_returns,
        "maturity_value": maturity_value,
        "multiplier": multiplier,
        "yearly_data": yearly_data
    }


def compute_health_score(app_data):
    """Compute financial health score (0-100) with breakdown."""
    score = 0
    breakdown = []
    data = app_data
    income = data["income"]["sources"][0]["amount"]
    expenses = sum(e["actual"] for e in data["expenses"]["categories"])
    savings = income - expenses
    savings_rate = (savings / income * 100) if income > 0 else 0
    
    try:
        ef_goal = next((g for g in data["savings_goals"] if "Emergency" in g["name"]), None)
    except:
        ef_goal = None
    ef_saved = ef_goal["saved"] if ef_goal else 0
    ef_months = ef_saved / expenses if expenses > 0 else 0
    
    loan_status = data["loan"]["status"]
    
    has_sip = data["income"]["sources"][0]["amount"] > 0 and any(
        "SIP" in g["name"] for g in data["savings_goals"]
    )
    
    if savings_rate >= 20:
        score += 25
        breakdown.append({"criterion": "Savings Rate >= 20%", "points": 25, "status": True, "detail": f"{savings_rate:.1f}%"})
    else:
        breakdown.append({"criterion": "Savings Rate >= 20%", "points": 0, "status": False, "detail": f"{savings_rate:.1f}%"})
    
    if ef_months >= 3:
        score += 25
        breakdown.append({"criterion": "Emergency Fund >= 3 months expenses", "points": 25, "status": True, "detail": f"{ef_months:.1f} months"})
    else:
        breakdown.append({"criterion": "Emergency Fund >= 3 months expenses", "points": 0, "status": False, "detail": f"{ef_months:.1f} months"})
    
    if loan_status == "Moratorium":
        score += 20
        breakdown.append({"criterion": "No Loan Overdue", "points": 20, "status": True, "detail": loan_status})
    else:
        breakdown.append({"criterion": "No Loan Overdue", "points": 20, "status": True, "detail": "Active EMI"})
    
    if expenses / income < 0.70 if income > 0 else False:
        score += 20
        breakdown.append({"criterion": "Expenses < 70% of Income", "points": 20, "status": True})
    else:
        breakdown.append({"criterion": "Expenses < 70% of Income", "points": 0, "status": False})
    
    if has_sip:
        score += 10
        breakdown.append({"criterion": "Active Investment/SIP", "points": 10, "status": True})
    else:
        breakdown.append({"criterion": "Active Investment/SIP", "points": 0, "status": False})
    
    if score >= 71:
        label = "Excellent"
    elif score >= 51:
        label = "Good"
    elif score >= 31:
        label = "Fair"
    else:
        label = "Needs Improvement"
    
    return {"score": score, "label": label, "breakdown": breakdown}


def compute_inhand_from_ctc(ctc_annual, basic_pct, hra_pct, special_pct, pf_pct, prof_tax, tax_bracket_pct):
    """Full salary breakdown from CTC."""
    basic = ctc_annual * basic_pct / 100
    hra = ctc_annual * hra_pct / 100
    special = ctc_annual * special_pct / 100
    gross = basic + hra + special
    pf_employee = basic * pf_pct / 100 / 12
    pf_employer = basic * pf_pct / 100 / 12
    prof_tax_monthly = prof_tax
    tds_annual = max(gross * tax_bracket_pct / 100, 0)
    tds_monthly = tds_annual / 12
    net_inhand = gross / 12 - pf_employee - prof_tax_monthly - tds_monthly
    return {
        "basic": round(basic, 2),
        "hra": round(hra, 2),
        "special_allowance": round(special, 2),
        "gross_annual": round(gross, 2),
        "pf_employee_monthly": round(pf_employee, 2),
        "pf_employer_monthly": round(pf_employer, 2),
        "professional_tax_monthly": prof_tax_monthly,
        "tds_annual": round(tds_annual, 2),
        "tds_monthly": round(tds_monthly, 2),
        "net_inhand_monthly": round(net_inhand, 2)
    }


# Aliases for backward/forward compatibility
# Pages may import with either 'compute_' or 'calculate_' prefix

def calculate_emi(principal, annual_rate, tenure_months):
    """Alias for compute_emi.*"""
    return compute_emi(principal, annual_rate, tenure_months)


def calculate_sip_maturity(monthly, annual_return_pct, years):
    """Alias for compute_sip_maturity.*"""
    return compute_sip_maturity(monthly, annual_return_pct, years)


def calculate_fd_maturity(principal, annual_rate, years):
    """Estimate FD maturity value (compound annually).*"""
    if annual_rate <= 0 or years <= 0 or principal <= 0:
        return {"maturity_value": principal, "interest_earned": 0.0, "total_return": 0.0}
    r = annual_rate / 100
    maturity_value = round(principal * ((1 + r) ** years), 2)
    interest_earned = round(maturity_value - principal, 2)
    total_return = round((interest_earned / principal) * 100, 2)
    return {
        "maturity_value": maturity_value,
        "interest_earned": interest_earned,
        "total_return": total_return
    }


def calculate_remaining_balance(principal, annual_rate, tenure_months, months_paid=0):
    """Estimate remaining balance after some months of EMI payments.*"""
    if months_paid <= 0:
        return round(principal, 2)
    r = annual_rate / 12 / 100
    n = tenure_months
    remaining = principal * ((1 + r) ** months_paid)
    if r > 0:
        emi = compute_emi(principal, annual_rate, n)
        paid = emi * ((1 + r) ** months_paid - 1) / r
        remaining = principal * ((1 + r) ** months_paid) - paid
    return round(max(remaining, 0), 2)

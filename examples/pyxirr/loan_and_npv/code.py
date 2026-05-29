# ---------------------------------------------------------------------
# Loan analysis with PMT, FV, NPV, and IRR
# ---------------------------------------------------------------------
#
# pyxirr ships the full numpy-financial-style suite. Let's price a
# car loan and then evaluate a small business project with NPV / IRR.

heading("Financing a $25,000 car over 5 years at 6.5% APR")

annual_rate = 0.065
periods = 5 * 12          # 60 monthly payments
periodic_rate = annual_rate / 12
loan_amount = 25_000

# pmt: the fixed monthly payment that pays the loan off exactly.
# Sign convention: present value (pv) is what you receive (+),
# and pmt comes out negative because you're paying it.
monthly_payment = pyxirr.pmt(periodic_rate, periods, loan_amount)
total_paid = -monthly_payment * periods
total_interest = total_paid - loan_amount

note(
    f"Monthly payment: <strong>${-monthly_payment:,.2f}</strong><br>"
    f"Total paid over 5 years: ${total_paid:,.2f}<br>"
    f"Total interest: ${total_interest:,.2f}"
)

# fv: the future value of a savings plan.
# What if instead of buying the car, you invested that monthly payment
# at 5% APR for the same 5 years?
future_value = pyxirr.fv(0.05 / 12, periods, monthly_payment, 0)
note(
    f"If you invested ${-monthly_payment:,.2f}/month at 5% APR "
    f"for 5 years, you'd have <strong>${future_value:,.2f}</strong>."
)

# ---------------------------------------------------------------------
# A small business project: should we open a second bakery branch?
# ---------------------------------------------------------------------
heading("Project appraisal: opening a second bakery")
note(
    "Year-0 build-out costs $40,000, then five years of net cash "
    "flows. We compare NPV at our 8% hurdle rate against IRR."
)

project_cash_flows = [-40_000, 9_000, 12_000, 15_000, 18_000, 14_000]

hurdle_rate = 0.08
npv = pyxirr.npv(hurdle_rate, project_cash_flows)
irr = pyxirr.irr(project_cash_flows)

verdict = "go ahead" if npv > 0 else "skip it"
note(
    f"NPV at {hurdle_rate:.0%}: <strong>${npv:,.2f}</strong> "
    f"(positive &rarr; {verdict}).<br>"
    f"IRR: <strong>{irr:.2%}</strong> "
    f"(beats the 8% hurdle by {irr - hurdle_rate:.2%})."
)

"""
Welcome to pyxirr! It's a Rust-powered toolbox of financial functions
for Python: XIRR, IRR, NPV, FV, and friends.

In this first example we compute the XIRR (extended internal rate of
return) of a small angel investment. XIRR is the annualized return on
a series of cash flows that occur on irregular dates -- the everyday
case for real-world investments.

Docs: https://anexen.github.io/pyxirr
"""
from datetime import date
from IPython.core.display import display, HTML
import pyxirr

heading("An angel investment in 'BrewCraft Coffee'")
note(
    "You put $10,000 into a tiny coffee roaster in early 2020. "
    "Over the next four years you take a few small distributions "
    "and finally exit with a $9,500 buyout. What was your annualized "
    "return?"
)

# Negative amounts are money out of your pocket; positive amounts are
# money you received. Dates can be irregular -- that's the whole point
# of XIRR vs. plain IRR.
cash_flow = [
    (date(2020, 2, 14), -10_000.00),  # initial investment
    (date(2021, 6, 30),     750.00),  # first distribution
    (date(2022, 9, 15),   1_200.00),  # second distribution
    (date(2023, 3,  1),     800.00),  # third distribution
    (date(2024, 5, 20),   9_500.00),  # exit / buyout
]

# pyxirr accepts many shapes. Here we pass an iterable of (date, amount)
# tuples; you can also pass parallel lists, a dict, a DataFrame, etc.
annualized_return = pyxirr.xirr(cash_flow)
note(f"XIRR (annualized return): <strong>{annualized_return:.2%}</strong>")

# XNPV tells you the present value of those flows at a chosen discount
# rate. At the XIRR rate, XNPV should be ~0 by definition.
npv_at_xirr = pyxirr.xnpv(annualized_return, cash_flow)
npv_at_8pct = pyxirr.xnpv(0.08, cash_flow)
note(
    f"XNPV at the XIRR rate: <code>{npv_at_xirr:,.4f}</code> "
    f"(should be ~0).<br>"
    f"XNPV if your hurdle rate were 8%: <code>{npv_at_8pct:,.2f}</code>."
)

# Show the cash flow itself for context.
rows = "".join(
    f"<tr><td>{d.isoformat()}</td><td style='text-align:right'>"
    f"{amount:,.2f}</td></tr>"
    for d, amount in cash_flow
)
display(HTML(
    "<table><thead><tr><th>Date</th><th>Amount ($)</th></tr></thead>"
    f"<tbody>{rows}</tbody></table>"
), append=True)

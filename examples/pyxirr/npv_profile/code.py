# ---------------------------------------------------------------------
# When IRR isn't unique: building an NPV profile
# ---------------------------------------------------------------------
#
# When a project's cash flows change sign more than once (e.g. a mine
# that needs cleanup costs at the end), there can be multiple IRRs --
# or none. pyxirr gives us tools to see this clearly.

heading("A mining project with cleanup costs")
note(
    "Year 0: $1.2M build-out (negative). Years 1-4: strong positive "
    "cash flows. Year 5: a large environmental cleanup obligation. "
    "The signs flip twice, so this is non-conventional."
)

cash_flows = [-1_200_000, 600_000, 700_000, 800_000, 500_000, -1_800_000]

# pyxirr exposes a quick check for sign-change count.
is_conventional = pyxirr.is_conventional_cash_flow(cash_flows)
note(
    f"Conventional cash flow? <strong>{is_conventional}</strong> "
    "(False means there could be multiple IRRs.)"
)

# Build an NPV profile: NPV evaluated across a sweep of discount rates.
rates = np.linspace(-0.20, 0.80, 200)
npvs = np.array([pyxirr.npv(r, cash_flows) for r in rates])

# pyxirr can find where NPV crosses zero -- those are the IRRs.
crossing_indexes = pyxirr.zero_crossing_points(npvs)

candidate_irrs = []
for idx in crossing_indexes:
    # Use the rate just before the crossing as a guess to refine.
    irr = pyxirr.irr(cash_flows, guess=rates[idx])
    candidate_irrs.append(irr)

note(
    "Zero crossings found at rates near: "
    + ", ".join(f"<strong>{r:.2%}</strong>" for r in candidate_irrs)
    + ". Each is a valid IRR for these cash flows."
)

# Plot the NPV profile and mark the crossings.
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(rates, npvs, color="steelblue", linewidth=2, label="NPV(rate)")
ax.axhline(0, color="black", linewidth=0.8)
for irr in candidate_irrs:
    ax.axvline(irr, color="crimson", linestyle="--", linewidth=1)
    ax.annotate(
        f"IRR = {irr:.2%}",
        xy=(irr, 0),
        xytext=(8, 12),
        textcoords="offset points",
        color="crimson",
    )
ax.set_title("NPV profile: a non-conventional project has multiple IRRs")
ax.set_xlabel("Discount rate")
ax.set_ylabel("NPV ($)")
ax.legend(loc="upper right")
fig.tight_layout()
display(fig, append=True)

note(
    "Takeaway: when IRR is ambiguous, prefer NPV at your actual cost "
    "of capital. The NPV profile makes the ambiguity visible."
)

# Catastrophe Loss Modeling & Insurance Program Optimization

**Author:** Ariel Farzan
**Tools:** Python (NumPy, SciPy, pandas, matplotlib)

A quantitative risk-modeling project that simulates a commercial real-estate
portfolio's annual catastrophe losses and recommends the most cost-effective
insurance program on a risk-adjusted basis. Built from a real loss run of 240+
historical claims across Fire, Named Windstorm, and Earthquake perils.

---

## What this does

1. **Loads & cleans** a historical loss run (trended ultimate losses by peril and location).
2. **Fits severity distributions** to fire losses — Lognormal vs. Gamma vs. Pareto —
   and selects the best fit using **AIC** and the **Kolmogorov-Smirnov** goodness-of-fit test.
   *Result: Lognormal (AIC 6,880; KS p = 0.43 — the only candidate that passes).*
3. **Runs a 100,000-year Monte Carlo simulation** of annual aggregate losses:
   - **Fire:** Poisson(λ = 15) frequency × fitted Lognormal severity.
   - **NWS / EQ:** discrete catastrophe-model frequencies × Pareto severities
     (parameterized from mean and coefficient of variation).
4. **Stress-tests three insurance programs** by applying each structure's
   retention, per-occurrence and aggregate limits, and coinsurance to the
   simulated losses, then compares them on **Premium, Total Retained, TCOR
   (Total Cost of Risk), and TVaR (Tail Value at Risk @ 95%)**.
5. **Produces exhibits** visualizing the loss distribution of each peril.

## Key results

| Metric | Value |
|---|---|
| Simulated mean annual total loss | **~$21M** |
| 95th-percentile annual total loss | **~$48M** |
| Selected fire severity model | **Lognormal** |
| Most cost-efficient program (lowest TCOR) | **Insurer 1** |
| Best tail protection (lowest TVaR) | **Insurer 2 / 3** |

The analysis shows why a median-based view understates risk: earthquake and
windstorm losses are heavy-tailed, so a **tail metric (TVaR)** is needed to
choose a program that protects against rare but catastrophic years.

## Files

- `cat_loss_model.py` — the full analysis (load → fit → simulate → compare → plot)
- `Loss_Run_20241231.xlsx` — historical loss data
- `exhibit_losses_by_peril.png` — simulated loss-distribution exhibit

## Run it

```bash
pip install numpy scipy pandas matplotlib openpyxl
python cat_loss_model.py
```

---

*Methodology note: severity fitting and aggregate-loss simulation follow standard
actuarial practice (collective risk model). The insurance-layer logic is a
simplified per-occurrence approximation suitable for portfolio-level program
comparison.*

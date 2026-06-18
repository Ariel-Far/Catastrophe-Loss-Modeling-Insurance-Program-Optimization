"""
Catastrophe Loss Modeling & Commercial Property Insurance Program Optimization
==============================================================================
Client: Montgomery Realty (commercial real estate portfolio: Tampa, San
Francisco, Chicago) exposed to Fire, Named Windstorm (NWS), and Earthquake (EQ).

Objective: Simulate the client's annual aggregate loss distribution across all
three perils, then stress-test three procured insurance programs to recommend
the most cost-effective structure on a risk-adjusted basis.

Method: severity-distribution fitting (Lognormal / Gamma / Pareto compared by
AIC and Kolmogorov-Smirnov), Monte Carlo aggregate-loss simulation, and program
comparison on Premium, Total Retained, TCOR, and Tail Value at Risk (TVaR).

Author: Ariel Farzan
"""

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

RNG = np.random.default_rng(42)      # reproducible
N_YEARS = 100_000                    # simulated years
DATA = "Loss_Run_20241231.xlsx"


# ----------------------------------------------------------------------
# 1. LOAD DATA
# ----------------------------------------------------------------------
def load_fire_losses(path=DATA):
    df = pd.read_excel(path, sheet_name="Sheet1")
    fire = df.loc[df["Type"] == "Fire", "Trended Ultimate Loss"].values
    return fire


# ----------------------------------------------------------------------
# 2. SEVERITY FIT  (Task 1.3)
#    Compare candidate distributions; select by AIC + KS goodness-of-fit.
# ----------------------------------------------------------------------
def fit_severity(fire):
    candidates = {
        "Lognormal": (stats.lognorm, stats.lognorm.fit(fire, floc=0)),
        "Gamma":     (stats.gamma,   stats.gamma.fit(fire, floc=0)),
        "Pareto":    (stats.pareto,  stats.pareto.fit(fire, floc=0)),
    }
    rows = []
    for name, (dist, params) in candidates.items():
        ll = np.sum(dist.logpdf(fire, *params))
        aic = 2 * len(params) - 2 * ll
        ks_d, ks_p = stats.kstest(fire, dist.cdf, args=params)
        rows.append((name, aic, ks_d, ks_p))
    table = pd.DataFrame(rows, columns=["Distribution", "AIC", "KS_D", "KS_p"])
    best = table.sort_values("AIC").iloc[0]["Distribution"]
    return table, best, candidates[best]


# ----------------------------------------------------------------------
# 3. MONTE CARLO SIMULATION  (Tasks 1.4 & 2.2)
#    Fire:  Poisson(15) frequency, fitted Lognormal severity.
#    NWS/EQ: discrete frequency + Pareto severity from CAT model output.
# ----------------------------------------------------------------------
def pareto_from_mean_cv(mean, cv, size, rng):
    """Sample a Pareto(alpha, xm) parameterised by target mean and CV."""
    # CV^2 = 1 / (alpha*(alpha-2))  ->  solve for alpha (> 2)
    cv2 = cv ** 2
    alpha = (1 + np.sqrt(1 + 4 / cv2)) / 2 + 1
    # mean = alpha*xm/(alpha-1)  ->  xm
    xm = mean * (alpha - 1) / alpha
    u = rng.random(size)
    return xm / (u ** (1 / alpha))      # inverse-CDF sample


def simulate(fire_dist, fire_params, n_years=N_YEARS, rng=RNG):
    # --- Fire ---
    n_fire = rng.poisson(15, n_years)
    fire_agg = np.array([
        fire_dist.rvs(*fire_params, size=k, random_state=rng).sum() if k else 0.0
        for k in n_fire
    ])

    # --- Named Windstorm: P(2)=.4, P(3)=.2, P(4)=.2, P(5)=.2 ---
    nws_counts = rng.choice([2, 3, 4, 5], size=n_years, p=[.4, .2, .2, .2])
    nws_agg = np.array([
        pareto_from_mean_cv(794_000, 3.7, k, rng).sum() for k in nws_counts
    ])

    # --- Earthquake: P(0)=.6, P(1)=.2, P(2)=.1, P(3)=.1 ---
    eq_counts = rng.choice([0, 1, 2, 3], size=n_years, p=[.6, .2, .1, .1])
    eq_agg = np.array([
        pareto_from_mean_cv(10_670_000, 34.5, k, rng).sum() if k else 0.0
        for k in eq_counts
    ])

    total = fire_agg + nws_agg + eq_agg
    return pd.DataFrame({"Fire": fire_agg, "NWS": nws_agg,
                         "EQ": eq_agg, "Total": total})


# ----------------------------------------------------------------------
# 4. INSURANCE PROGRAM STRESS TEST  (Tasks 3 & 4)
#    Apply each program's retention / limits / aggregate / coinsurance to the
#    simulated losses and compute what the policyholder RETAINS each year.
# ----------------------------------------------------------------------
PROGRAMS = {
    "Insurer 1": dict(retention=10e6, fire_limit=1e9, fire_coins=0.0,
                      nws_occ=100e6, nws_agg=100e6, eq_occ=500e6, premium=51_270_000),
    "Insurer 2": dict(retention=10e6, fire_limit=1e9, fire_coins=0.0,
                      nws_occ=100e6, nws_agg=None,  eq_occ=1e9,  premium=54_095_800),
    "Insurer 3": dict(retention=1e6,  fire_limit=1e9, fire_coins=0.30,
                      nws_occ=100e6, nws_agg=100e6, eq_occ=1e9,  premium=59_411_000),
}


def retained_total(sim, prog, rng=RNG):
    """
    Approximate annual policyholder-retained loss under one program.
    Fire is excess of a per-occurrence retention; NWS/EQ have no retention but
    per-occurrence (and possibly aggregate) limits. Coinsurance applies within
    the insured fire layer. This mirrors the case's Total Retained definition:
    retention layer + excess-of-limits.
    """
    ret = prog["retention"]
    # Fire: policyholder keeps the retention layer + coinsurance share of insured layer
    fire_insured = np.clip(sim["Fire"].values - ret, 0, prog["fire_limit"])
    fire_retained = np.minimum(sim["Fire"].values, ret) \
        + fire_insured * prog["fire_coins"] \
        + np.clip(sim["Fire"].values - ret - prog["fire_limit"], 0, None)

    # NWS: no retention; insurer covers up to occurrence/aggregate limit
    nws_cap = prog["nws_agg"] if prog["nws_agg"] else prog["nws_occ"]
    nws_retained = np.clip(sim["NWS"].values - nws_cap, 0, None)

    # EQ: no retention; insurer covers up to occurrence limit
    eq_retained = np.clip(sim["EQ"].values - prog["eq_occ"], 0, None)

    return fire_retained + nws_retained + eq_retained


def program_metrics(sim):
    rows = []
    for name, prog in PROGRAMS.items():
        retained = retained_total(sim, prog)
        avg_ret = retained.mean()
        med_ret = np.median(retained)
        tvar95 = retained[retained >= np.quantile(retained, 0.95)].mean()
        tcor = avg_ret + prog["premium"]
        rows.append((name, prog["premium"], avg_ret, med_ret, tvar95, tcor))
    return pd.DataFrame(rows, columns=[
        "Program", "Premium", "Avg Retained", "Median Retained",
        "TVaR 95", "TCOR"])


# ----------------------------------------------------------------------
# 5. EXHIBITS
# ----------------------------------------------------------------------
def make_exhibits(sim, fit_table, outdir="/home/claude"):
    # Loss distribution by peril
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, col, color in zip(axes.flat, ["Fire", "NWS", "EQ", "Total"],
                              ["#c0392b", "#2980b9", "#27ae60", "#8e44ad"]):
        data = sim[col].values / 1e6
        ax.hist(data, bins=80, color=color, edgecolor="white", linewidth=0.3)
        ax.set_title(f"Annual Aggregate {col} Loss", fontweight="bold")
        ax.set_xlabel("Loss ($M)")
        ax.set_ylabel("Frequency")
        ax.axvline(data.mean(), color="black", ls="--", lw=1,
                   label=f"Mean ${data.mean():.1f}M")
        ax.axvline(np.quantile(data, .95), color="gray", ls=":", lw=1,
                   label=f"95th ${np.quantile(data,.95):.1f}M")
        ax.legend(fontsize=8)
    fig.suptitle("Montgomery Realty — Simulated Annual Aggregate Losses by Peril",
                 fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(f"{outdir}/exhibit_losses_by_peril.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
if __name__ == "__main__":
    fire = load_fire_losses()
    print(f"Loaded {len(fire)} fire claims "
          f"(mean ${fire.mean():,.0f}, median ${np.median(fire):,.0f}).\n")

    fit_table, best, (best_dist, best_params) = fit_severity(fire)
    print("SEVERITY FIT — Fire losses")
    print(fit_table.to_string(index=False,
          formatters={"AIC": "{:.1f}".format, "KS_D": "{:.4f}".format,
                      "KS_p": "{:.4f}".format}))
    print(f"\nSelected severity distribution: {best} "
          f"(lowest AIC, passes KS).\n")

    sim = simulate(best_dist, best_params)
    summary = sim.agg(["mean", "median", "std"]).T
    summary["p95"] = sim.quantile(0.95)
    summary["p99"] = sim.quantile(0.99)
    print("SIMULATED ANNUAL AGGREGATE LOSS ($M)")
    print((summary / 1e6).to_string(
        float_format=lambda x: f"{x:,.2f}"))
    print()

    metrics = program_metrics(sim)
    print("INSURANCE PROGRAM COMPARISON ($)")
    print(metrics.to_string(index=False,
          float_format=lambda x: f"{x:,.0f}"))
    print()

    best_tcor = metrics.loc[metrics["TCOR"].idxmin(), "Program"]
    best_tvar = metrics.loc[metrics["TVaR 95"].idxmin(), "Program"]
    print(f"Lowest TCOR (cost-efficient): {best_tcor}")
    print(f"Lowest TVaR 95 (tail protection): {best_tvar}")

    make_exhibits(sim, fit_table)
    print("\nExhibit saved: exhibit_losses_by_peril.png")

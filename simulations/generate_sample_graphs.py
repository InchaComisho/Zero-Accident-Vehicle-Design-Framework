#!/usr/bin/env python3
"""Generate illustrative sample graphs for the adoption scenario simulator.

Requires matplotlib. If matplotlib is not available, this script prints a clear
message and exits without error so the repository remains functional.
"""

from __future__ import annotations

import os
import sys

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# ---------------------------------------------------------------------------
# Inline simulation — mirrors adoption_scenario_simulator.py logic exactly
# so this script can run standalone without importing the simulator module.
# ---------------------------------------------------------------------------

BASELINE_ACCIDENTS = 100_000.0
BASELINE_FATALITIES = 1_000.0
BASELINE_SEVERE_INJURIES = 5_000.0
BASELINE_MINOR_INJURIES = 30_000.0
YEARS = 20
GRADUAL_FINAL_ADOPTION = 0.8
FULL_ADOPTION = 1.0
ANNUAL_RISK_GROWTH = 0.0
ACCIDENT_REDUCTION_EFFECT = 0.35
FATALITY_REDUCTION_EFFECT = 0.80
SEVERE_INJURY_REDUCTION_EFFECT = 0.70
MINOR_INJURY_REDUCTION_EFFECT = 0.20
SEVERITY_SHIFT_FACTOR = 0.30
INTERACTION_CAP = 0.90

IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")

DISCLAIMER_NOTE = (
    "Illustrative assumption-based output only.\n"
    "Not a certified safety forecast. Not a guarantee.\n"
    "Requires real-world validation."
)


def _capped(value: float, cap: float) -> float:
    return min(value, cap)


def _estimate(adjusted_accidents: float, adjusted_fatalities: float,
              adjusted_severe: float, adjusted_minor: float,
              adoption_rate: float):
    eff_acc = _capped(adoption_rate * ACCIDENT_REDUCTION_EFFECT, INTERACTION_CAP)
    eff_fat = _capped(adoption_rate * FATALITY_REDUCTION_EFFECT, INTERACTION_CAP)
    eff_sev = _capped(adoption_rate * SEVERE_INJURY_REDUCTION_EFFECT, INTERACTION_CAP)
    eff_min = _capped(adoption_rate * MINOR_INJURY_REDUCTION_EFFECT, INTERACTION_CAP)

    fat_after = adjusted_fatalities * (1.0 - eff_fat)
    sev_after = adjusted_severe * (1.0 - eff_sev)
    min_after_base = adjusted_minor * (1.0 - eff_min)

    fat_prevented = adjusted_fatalities - fat_after
    sev_prevented = adjusted_severe - sev_after
    shifted = (fat_prevented + sev_prevented) * SEVERITY_SHIFT_FACTOR

    return (
        adjusted_accidents * (1.0 - eff_acc),
        fat_after,
        sev_after,
        min_after_base + shifted,
    )


def simulate():
    denominator = max(YEARS - 1, 1)
    years = list(range(1, YEARS + 1))

    no_acc, no_fat, no_sev, no_min = [], [], [], []
    grad_acc, grad_fat, grad_sev, grad_min, grad_rates = [], [], [], [], []
    full_acc, full_fat, full_sev, full_min = [], [], [], []

    cum_no_fat = cum_no_sev = 0.0
    cum_grad_fat = cum_grad_sev = 0.0
    cum_full_fat = cum_full_sev = 0.0

    cum_no_acc = cum_grad_acc = cum_full_acc = 0.0

    prev_no_fat_list, prev_grad_fat_list, prev_full_fat_list = [], [], []
    prev_no_sev_list, prev_grad_sev_list, prev_full_sev_list = [], [], []

    for year in years:
        gm = (1.0 + ANNUAL_RISK_GROWTH) ** (year - 1)
        ba = BASELINE_ACCIDENTS * gm
        bf = BASELINE_FATALITIES * gm
        bs = BASELINE_SEVERE_INJURIES * gm
        bm = BASELINE_MINOR_INJURIES * gm

        na, nf, ns, nm = _estimate(ba, bf, bs, bm, 0.0)
        no_acc.append(na); no_fat.append(nf); no_sev.append(ns); no_min.append(nm)

        rate = GRADUAL_FINAL_ADOPTION * ((year - 1) / denominator)
        grad_rates.append(rate)
        ga, gf, gs, gm_ = _estimate(ba, bf, bs, bm, rate)
        grad_acc.append(ga); grad_fat.append(gf); grad_sev.append(gs); grad_min.append(gm_)

        fa, ff, fs, fm = _estimate(ba, bf, bs, bm, FULL_ADOPTION)
        full_acc.append(fa); full_fat.append(ff); full_sev.append(fs); full_min.append(fm)

        cum_no_fat += nf; cum_no_sev += ns; cum_no_acc += na
        cum_grad_fat += gf; cum_grad_sev += gs; cum_grad_acc += ga
        cum_full_fat += ff; cum_full_sev += fs; cum_full_acc += fa

        prev_no_fat_list.append(cum_no_fat)
        prev_grad_fat_list.append(cum_grad_fat)
        prev_full_fat_list.append(cum_full_fat)
        prev_no_sev_list.append(cum_no_sev)
        prev_grad_sev_list.append(cum_grad_sev)
        prev_full_sev_list.append(cum_full_sev)

    # cumulative prevented
    cum_prevented_grad_fat = [prev_no_fat_list[i] - prev_grad_fat_list[i] for i in range(YEARS)]
    cum_prevented_full_fat = [prev_no_fat_list[i] - prev_full_fat_list[i] for i in range(YEARS)]
    cum_prevented_grad_sev = [prev_no_sev_list[i] - prev_grad_sev_list[i] for i in range(YEARS)]
    cum_prevented_full_sev = [prev_no_sev_list[i] - prev_full_sev_list[i] for i in range(YEARS)]

    return {
        "years": years,
        "no_acc": no_acc, "no_fat": no_fat, "no_sev": no_sev, "no_min": no_min,
        "grad_acc": grad_acc, "grad_fat": grad_fat, "grad_sev": grad_sev, "grad_min": grad_min,
        "full_acc": full_acc, "full_fat": full_fat, "full_sev": full_sev, "full_min": full_min,
        "cum_prevented_grad_fat": cum_prevented_grad_fat,
        "cum_prevented_full_fat": cum_prevented_full_fat,
        "cum_prevented_grad_sev": cum_prevented_grad_sev,
        "cum_prevented_full_sev": cum_prevented_full_sev,
    }


def add_disclaimer(ax):
    ax.text(
        0.5, -0.18, DISCLAIMER_NOTE,
        transform=ax.transAxes,
        fontsize=7, color="#888888",
        ha="center", va="top",
        style="italic",
        wrap=True,
    )


def save(fig, filename):
    os.makedirs(IMAGES_DIR, exist_ok=True)
    path = os.path.join(IMAGES_DIR, filename)
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_fatalities(data):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(data["years"], data["no_fat"], color="#c0392b", linewidth=2,
            marker="o", markersize=3, label="No adoption")
    ax.plot(data["years"], data["grad_fat"], color="#e67e22", linewidth=2,
            marker="s", markersize=3, label="Gradual adoption (0→80%)")
    ax.plot(data["years"], data["full_fat"], color="#27ae60", linewidth=2,
            marker="^", markersize=3, label="Full adoption (100%)")
    ax.set_title("Illustrative Scenario Output — Annual Fatalities by Adoption Pathway", fontsize=12)
    ax.set_xlabel("Year")
    ax.set_ylabel("Estimated Annual Fatalities (illustrative)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1, YEARS)
    add_disclaimer(ax)
    save(fig, "adoption_scenario_fatalities.png")


def plot_severe_injuries(data):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(data["years"], data["no_sev"], color="#c0392b", linewidth=2,
            marker="o", markersize=3, label="No adoption")
    ax.plot(data["years"], data["grad_sev"], color="#e67e22", linewidth=2,
            marker="s", markersize=3, label="Gradual adoption (0→80%)")
    ax.plot(data["years"], data["full_sev"], color="#27ae60", linewidth=2,
            marker="^", markersize=3, label="Full adoption (100%)")
    ax.set_title("Illustrative Scenario Output — Annual Severe Injuries by Adoption Pathway", fontsize=12)
    ax.set_xlabel("Year")
    ax.set_ylabel("Estimated Annual Severe Injuries (illustrative)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1, YEARS)
    add_disclaimer(ax)
    save(fig, "adoption_scenario_severe_injuries.png")


def plot_total_accidents(data):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(data["years"], data["no_acc"], color="#c0392b", linewidth=2,
            marker="o", markersize=3, label="No adoption")
    ax.plot(data["years"], data["grad_acc"], color="#e67e22", linewidth=2,
            marker="s", markersize=3, label="Gradual adoption (0→80%)")
    ax.plot(data["years"], data["full_acc"], color="#27ae60", linewidth=2,
            marker="^", markersize=3, label="Full adoption (100%)")
    ax.set_title("Illustrative Scenario Output — Annual Total Accidents by Adoption Pathway", fontsize=12)
    ax.set_xlabel("Year")
    ax.set_ylabel("Estimated Annual Total Accidents (illustrative)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1, YEARS)
    add_disclaimer(ax)
    save(fig, "adoption_scenario_total_accidents.png")


def plot_cumulative_prevented(data):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(data["years"], data["cum_prevented_grad_fat"], color="#e67e22", linewidth=2,
            marker="s", markersize=3, linestyle="--", label="Prevented fatalities — gradual adoption")
    ax.plot(data["years"], data["cum_prevented_full_fat"], color="#27ae60", linewidth=2,
            marker="^", markersize=3, linestyle="--", label="Prevented fatalities — full adoption")
    ax.plot(data["years"], data["cum_prevented_grad_sev"], color="#e67e22", linewidth=2,
            marker="s", markersize=3, linestyle="-", label="Prevented severe injuries — gradual adoption")
    ax.plot(data["years"], data["cum_prevented_full_sev"], color="#27ae60", linewidth=2,
            marker="^", markersize=3, linestyle="-", label="Prevented severe injuries — full adoption")
    ax.set_title("Illustrative Scenario Output — Cumulative Prevented Fatalities and Severe Injuries", fontsize=11)
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative illustrative prevented outcomes")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1, YEARS)
    add_disclaimer(ax)
    save(fig, "adoption_scenario_cumulative_prevented.png")


def main():
    if not MATPLOTLIB_AVAILABLE:
        print(
            "matplotlib is not available in this environment.\n"
            "Install it with: pip install matplotlib\n"
            "Graph generation skipped. The repository remains functional without graphs."
        )
        return

    print("Generating illustrative sample graphs...")
    data = simulate()
    plot_fatalities(data)
    plot_severe_injuries(data)
    plot_total_accidents(data)
    plot_cumulative_prevented(data)
    print("All graphs generated.")
    print(f"Output directory: {IMAGES_DIR}")
    print()
    print("Note: All graphs are illustrative assumption-based outputs.")
    print("They are not certified safety forecasts and do not guarantee any outcome.")


if __name__ == "__main__":
    main()

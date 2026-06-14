#!/usr/bin/env python3
"""Severity-aware adoption scenario simulator for conceptual comparison."""

from __future__ import annotations

import argparse
from dataclasses import dataclass


DISCLAIMER = """This is an illustrative assumption-based severity-aware scenario model.
It is not a certified safety forecast.
It does not guarantee accident, fatality, or severe-injury reduction.
Real-world outcomes require empirical traffic data, regional validation, legal review, and safety engineering."""


@dataclass(frozen=True)
class Outcome:
    accidents: float
    fatalities: float
    severe_injuries: float
    minor_injuries: float

    def __add__(self, other: "Outcome") -> "Outcome":
        return Outcome(
            self.accidents + other.accidents,
            self.fatalities + other.fatalities,
            self.severe_injuries + other.severe_injuries,
            self.minor_injuries + other.minor_injuries,
        )

    def __sub__(self, other: "Outcome") -> "Outcome":
        return Outcome(
            self.accidents - other.accidents,
            self.fatalities - other.fatalities,
            self.severe_injuries - other.severe_injuries,
            self.minor_injuries - other.minor_injuries,
        )


ZERO_OUTCOME = Outcome(0.0, 0.0, 0.0, 0.0)


def bounded_rate(value: float, name: str) -> float:
    if not 0.0 <= value <= 1.0:
        raise argparse.ArgumentTypeError(f"{name} must be between 0 and 1")
    return value


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return parsed


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be at least 1")
    return parsed


def rate_arg(name: str):
    return lambda value: bounded_rate(float(value), name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a severity-aware conceptual scenario model comparing no adoption, "
            "gradual adoption, and full adoption pathways."
        )
    )
    parser.add_argument("--baseline-accidents", type=positive_float, default=100000.0)
    parser.add_argument("--baseline-fatalities", type=positive_float, default=1000.0)
    parser.add_argument("--baseline-severe-injuries", type=positive_float, default=5000.0)
    parser.add_argument("--baseline-minor-injuries", type=positive_float, default=30000.0)
    parser.add_argument("--years", type=positive_int, default=20)
    parser.add_argument("--gradual-final-adoption", type=rate_arg("gradual-final-adoption"), default=0.8)
    parser.add_argument("--full-adoption", type=rate_arg("full-adoption"), default=1.0)
    parser.add_argument("--annual-risk-growth", type=float, default=0.0)
    parser.add_argument("--accident-reduction-effect", type=rate_arg("accident-reduction-effect"), default=0.35)
    parser.add_argument("--fatality-reduction-effect", type=rate_arg("fatality-reduction-effect"), default=0.80)
    parser.add_argument(
        "--severe-injury-reduction-effect",
        type=rate_arg("severe-injury-reduction-effect"),
        default=0.70,
    )
    parser.add_argument("--minor-injury-reduction-effect", type=rate_arg("minor-injury-reduction-effect"), default=0.20)
    parser.add_argument("--severity-shift-factor", type=rate_arg("severity-shift-factor"), default=0.30)
    parser.add_argument("--interaction-cap", type=rate_arg("interaction-cap"), default=0.90)
    return parser


def capped(value: float, cap: float) -> float:
    return min(value, cap)


def estimate(args: argparse.Namespace, adjusted: Outcome, adoption_rate: float) -> Outcome:
    effective_accident_reduction = capped(adoption_rate * args.accident_reduction_effect, args.interaction_cap)
    effective_fatality_reduction = capped(adoption_rate * args.fatality_reduction_effect, args.interaction_cap)
    effective_severe_reduction = capped(adoption_rate * args.severe_injury_reduction_effect, args.interaction_cap)
    effective_minor_reduction = capped(adoption_rate * args.minor_injury_reduction_effect, args.interaction_cap)

    fatalities_after = adjusted.fatalities * (1.0 - effective_fatality_reduction)
    severe_after = adjusted.severe_injuries * (1.0 - effective_severe_reduction)
    minor_after_base = adjusted.minor_injuries * (1.0 - effective_minor_reduction)

    fatalities_prevented = adjusted.fatalities - fatalities_after
    severe_prevented = adjusted.severe_injuries - severe_after
    shifted_to_minor = (fatalities_prevented + severe_prevented) * args.severity_shift_factor

    return Outcome(
        accidents=adjusted.accidents * (1.0 - effective_accident_reduction),
        fatalities=fatalities_after,
        severe_injuries=severe_after,
        minor_injuries=minor_after_base + shifted_to_minor,
    )


def adjusted_baseline(args: argparse.Namespace, year: int) -> Outcome:
    growth_multiplier = (1.0 + args.annual_risk_growth) ** (year - 1)
    return Outcome(
        accidents=args.baseline_accidents * growth_multiplier,
        fatalities=args.baseline_fatalities * growth_multiplier,
        severe_injuries=args.baseline_severe_injuries * growth_multiplier,
        minor_injuries=args.baseline_minor_injuries * growth_multiplier,
    )


def format_number(value: float) -> str:
    return f"{value:,.1f}"


def print_difference(label: str, diff: Outcome) -> None:
    print(
        f"- {label}: "
        f"{format_number(diff.accidents)} accidents, "
        f"{format_number(diff.fatalities)} fatalities, "
        f"{format_number(diff.severe_injuries)} severe injuries, "
        f"{format_number(diff.minor_injuries)} minor injuries"
    )


def run(args: argparse.Namespace) -> None:
    print(DISCLAIMER)
    print()
    print("Assumption summary")
    print(f"- Gradual final adoption: {args.gradual_final_adoption:.1%}")
    print(f"- Full adoption: {args.full_adoption:.1%}")
    print(f"- Annual background risk growth: {args.annual_risk_growth:.2%}")
    print(f"- Interaction cap per outcome category: {args.interaction_cap:.1%}")
    print(f"- Severity shift factor: {args.severity_shift_factor:.1%}")
    print()
    print(
        "Note: injury categories are illustrative person-outcome categories, "
        "not necessarily one-to-one with crash counts."
    )
    print()

    header = (
        "Year | Grad adopt | No accidents | No fatal | No severe | No minor | "
        "Grad accidents | Grad fatal | Grad severe | Grad minor | "
        "Full accidents | Full fatal | Full severe | Full minor"
    )
    print(header)
    print("-" * len(header))

    cumulative_no = ZERO_OUTCOME
    cumulative_gradual = ZERO_OUTCOME
    cumulative_full = ZERO_OUTCOME

    denominator = max(args.years - 1, 1)
    for year in range(1, args.years + 1):
        adjusted = adjusted_baseline(args, year)
        no_adoption = estimate(args, adjusted, 0.0)
        gradual_rate = args.gradual_final_adoption * ((year - 1) / denominator)
        gradual = estimate(args, adjusted, gradual_rate)
        full = estimate(args, adjusted, args.full_adoption)

        cumulative_no = cumulative_no + no_adoption
        cumulative_gradual = cumulative_gradual + gradual
        cumulative_full = cumulative_full + full

        print(
            f"{year:>4} | "
            f"{gradual_rate:>10.1%} | "
            f"{format_number(no_adoption.accidents):>12} | "
            f"{format_number(no_adoption.fatalities):>8} | "
            f"{format_number(no_adoption.severe_injuries):>9} | "
            f"{format_number(no_adoption.minor_injuries):>8} | "
            f"{format_number(gradual.accidents):>14} | "
            f"{format_number(gradual.fatalities):>10} | "
            f"{format_number(gradual.severe_injuries):>11} | "
            f"{format_number(gradual.minor_injuries):>10} | "
            f"{format_number(full.accidents):>14} | "
            f"{format_number(full.fatalities):>10} | "
            f"{format_number(full.severe_injuries):>11} | "
            f"{format_number(full.minor_injuries):>10}"
        )

    print()
    print("Cumulative estimated differences over selected years")
    print_difference("No adoption minus gradual adoption", cumulative_no - cumulative_gradual)
    print_difference("No adoption minus full adoption", cumulative_no - cumulative_full)
    print_difference("Gradual adoption minus full adoption", cumulative_gradual - cumulative_full)
    print()
    print(DISCLAIMER)


def main() -> None:
    parser = build_parser()
    run(parser.parse_args())


if __name__ == "__main__":
    main()

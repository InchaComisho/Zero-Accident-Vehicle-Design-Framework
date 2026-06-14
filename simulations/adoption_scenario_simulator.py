#!/usr/bin/env python3
"""Compare conceptual adoption pathways for structural accident-risk reduction."""

from __future__ import annotations

import argparse
from dataclasses import dataclass


DISCLAIMER = """This is an illustrative assumption-based scenario model.
It is not a certified safety forecast.
It does not guarantee accident or fatality reduction.
Real-world outcomes require empirical traffic data, regional validation, legal review, and safety engineering."""


@dataclass(frozen=True)
class ScenarioResult:
    accidents: float
    fatalities: float


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
            "Run a conceptual scenario model comparing no adoption, gradual "
            "adoption, and full adoption pathways."
        )
    )
    parser.add_argument("--baseline-accidents", type=positive_float, default=100000.0)
    parser.add_argument("--baseline-fatalities", type=positive_float, default=1000.0)
    parser.add_argument("--years", type=positive_int, default=20)
    parser.add_argument("--gradual-final-adoption", type=rate_arg("gradual-final-adoption"), default=0.8)
    parser.add_argument("--full-adoption", type=rate_arg("full-adoption"), default=1.0)
    parser.add_argument("--annual-risk-growth", type=float, default=0.0)
    parser.add_argument("--speed-governance-effect", type=rate_arg("speed-governance-effect"), default=0.25)
    parser.add_argument("--driver-monitoring-effect", type=rate_arg("driver-monitoring-effect"), default=0.10)
    parser.add_argument(
        "--vulnerable-user-detection-effect",
        type=rate_arg("vulnerable-user-detection-effect"),
        default=0.15,
    )
    parser.add_argument(
        "--infrastructure-cooperation-effect",
        type=rate_arg("infrastructure-cooperation-effect"),
        default=0.10,
    )
    parser.add_argument(
        "--weather-context-control-effect",
        type=rate_arg("weather-context-control-effect"),
        default=0.05,
    )
    parser.add_argument("--interaction-cap", type=rate_arg("interaction-cap"), default=0.60)
    return parser


def capped_combined_effect(args: argparse.Namespace) -> float:
    total = (
        args.speed_governance_effect
        + args.driver_monitoring_effect
        + args.vulnerable_user_detection_effect
        + args.infrastructure_cooperation_effect
        + args.weather_context_control_effect
    )
    return min(total, args.interaction_cap)


def estimate(base_accidents: float, base_fatalities: float, adoption: float, combined_effect: float) -> ScenarioResult:
    effective_reduction = adoption * combined_effect
    multiplier = max(0.0, 1.0 - effective_reduction)
    return ScenarioResult(
        accidents=base_accidents * multiplier,
        fatalities=base_fatalities * multiplier,
    )


def format_number(value: float) -> str:
    return f"{value:,.1f}"


def run(args: argparse.Namespace) -> None:
    combined = capped_combined_effect(args)
    print(DISCLAIMER)
    print()
    print("Assumption summary")
    print(f"- Combined assumed risk-reduction potential before adoption: {combined:.1%}")
    print(f"- Gradual final adoption: {args.gradual_final_adoption:.1%}")
    print(f"- Full adoption: {args.full_adoption:.1%}")
    print(f"- Annual background risk growth: {args.annual_risk_growth:.2%}")
    print()

    header = (
        "Year | No adoption accidents | No adoption fatalities | "
        "Gradual accidents | Gradual fatalities | Full accidents | Full fatalities"
    )
    print(header)
    print("-" * len(header))

    cumulative_no = ScenarioResult(0.0, 0.0)
    cumulative_gradual = ScenarioResult(0.0, 0.0)
    cumulative_full = ScenarioResult(0.0, 0.0)

    denominator = max(args.years - 1, 1)
    for year in range(1, args.years + 1):
        growth_multiplier = (1.0 + args.annual_risk_growth) ** (year - 1)
        base_accidents = args.baseline_accidents * growth_multiplier
        base_fatalities = args.baseline_fatalities * growth_multiplier

        no_adoption = estimate(base_accidents, base_fatalities, 0.0, combined)
        gradual_adoption_rate = args.gradual_final_adoption * ((year - 1) / denominator)
        gradual = estimate(base_accidents, base_fatalities, gradual_adoption_rate, combined)
        full = estimate(base_accidents, base_fatalities, args.full_adoption, combined)

        cumulative_no = ScenarioResult(
            cumulative_no.accidents + no_adoption.accidents,
            cumulative_no.fatalities + no_adoption.fatalities,
        )
        cumulative_gradual = ScenarioResult(
            cumulative_gradual.accidents + gradual.accidents,
            cumulative_gradual.fatalities + gradual.fatalities,
        )
        cumulative_full = ScenarioResult(
            cumulative_full.accidents + full.accidents,
            cumulative_full.fatalities + full.fatalities,
        )

        print(
            f"{year:>4} | "
            f"{format_number(no_adoption.accidents):>21} | "
            f"{format_number(no_adoption.fatalities):>22} | "
            f"{format_number(gradual.accidents):>17} | "
            f"{format_number(gradual.fatalities):>18} | "
            f"{format_number(full.accidents):>14} | "
            f"{format_number(full.fatalities):>15}"
        )

    print()
    print("Cumulative scenario differences over selected years")
    print(
        "- No adoption minus gradual adoption: "
        f"{format_number(cumulative_no.accidents - cumulative_gradual.accidents)} accidents, "
        f"{format_number(cumulative_no.fatalities - cumulative_gradual.fatalities)} fatalities"
    )
    print(
        "- No adoption minus full adoption: "
        f"{format_number(cumulative_no.accidents - cumulative_full.accidents)} accidents, "
        f"{format_number(cumulative_no.fatalities - cumulative_full.fatalities)} fatalities"
    )
    print(
        "- Gradual adoption minus full adoption: "
        f"{format_number(cumulative_gradual.accidents - cumulative_full.accidents)} accidents, "
        f"{format_number(cumulative_gradual.fatalities - cumulative_full.fatalities)} fatalities"
    )
    print()
    print(DISCLAIMER)


def main() -> None:
    parser = build_parser()
    run(parser.parse_args())


if __name__ == "__main__":
    main()

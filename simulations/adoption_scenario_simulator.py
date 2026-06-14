#!/usr/bin/env python3
"""Severity-aware adoption scenario simulator for conceptual comparison."""

from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass
from typing import List, Optional


DISCLAIMER = """This is an illustrative assumption-based severity-aware scenario model.
It is not a certified safety forecast.
It does not guarantee accident, fatality, or severe-injury reduction.
Real-world outcomes require empirical traffic data, regional validation, legal review, and safety engineering."""

MARKDOWN_DISCLAIMER = """\
> **Disclaimer:** This is an illustrative assumption-based scenario output.
> It is not a certified safety forecast and does not guarantee accident, fatality,
> or severe-injury reduction. Real-world outcomes depend on baseline traffic data,
> adoption rates, road design, driver behavior, weather, vehicle fleet composition,
> regulation, infrastructure quality, and sensor reliability.
> Real-world validation is required before any safety claim can be made.
"""


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


@dataclass
class YearRow:
    year: int
    no_adoption_rate: float
    no_adoption_accidents: float
    no_adoption_fatalities: float
    no_adoption_severe_injuries: float
    no_adoption_minor_injuries: float
    gradual_adoption_rate: float
    gradual_accidents: float
    gradual_fatalities: float
    gradual_severe_injuries: float
    gradual_minor_injuries: float
    full_adoption_rate: float
    full_accidents: float
    full_fatalities: float
    full_severe_injuries: float
    full_minor_injuries: float


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
    parser.add_argument("--output-csv", type=str, default=None, metavar="PATH",
                        help="Export year-by-year results to CSV file")
    parser.add_argument("--output-markdown", type=str, default=None, metavar="PATH",
                        help="Export year-by-year results to Markdown file")
    parser.add_argument("--output-summary-json", type=str, default=None, metavar="PATH",
                        help="Export cumulative summary to JSON file")
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


def ensure_dir(path: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def export_csv(rows: List[YearRow], path: str) -> None:
    ensure_dir(path)
    fieldnames = [
        "year",
        "no_adoption_accidents",
        "no_adoption_fatalities",
        "no_adoption_severe_injuries",
        "no_adoption_minor_injuries",
        "gradual_adoption_rate",
        "gradual_accidents",
        "gradual_fatalities",
        "gradual_severe_injuries",
        "gradual_minor_injuries",
        "full_adoption_rate",
        "full_accidents",
        "full_fatalities",
        "full_severe_injuries",
        "full_minor_injuries",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "year": row.year,
                "no_adoption_accidents": round(row.no_adoption_accidents, 1),
                "no_adoption_fatalities": round(row.no_adoption_fatalities, 1),
                "no_adoption_severe_injuries": round(row.no_adoption_severe_injuries, 1),
                "no_adoption_minor_injuries": round(row.no_adoption_minor_injuries, 1),
                "gradual_adoption_rate": round(row.gradual_adoption_rate, 6),
                "gradual_accidents": round(row.gradual_accidents, 1),
                "gradual_fatalities": round(row.gradual_fatalities, 1),
                "gradual_severe_injuries": round(row.gradual_severe_injuries, 1),
                "gradual_minor_injuries": round(row.gradual_minor_injuries, 1),
                "full_adoption_rate": round(row.full_adoption_rate, 6),
                "full_accidents": round(row.full_accidents, 1),
                "full_fatalities": round(row.full_fatalities, 1),
                "full_severe_injuries": round(row.full_severe_injuries, 1),
                "full_minor_injuries": round(row.full_minor_injuries, 1),
            })
    print(f"CSV exported: {path}")


def export_markdown(rows: List[YearRow], args: argparse.Namespace,
                    cumulative_no: Outcome, cumulative_gradual: Outcome,
                    cumulative_full: Outcome, path: str) -> None:
    ensure_dir(path)
    diff_no_vs_gradual = cumulative_no - cumulative_gradual
    diff_no_vs_full = cumulative_no - cumulative_full
    diff_gradual_vs_full = cumulative_gradual - cumulative_full

    lines = []
    lines.append("# Sample Adoption Scenario Results")
    lines.append("")
    lines.append("This is an illustrative assumption-based scenario output.")
    lines.append("It is not a certified safety forecast and does not guarantee accident, fatality, or severe-injury reduction.")
    lines.append("")
    lines.append(MARKDOWN_DISCLAIMER)
    lines.append("")
    lines.append("## Assumptions")
    lines.append("")
    lines.append(f"| Parameter | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Baseline annual accidents | {args.baseline_accidents:,.0f} |")
    lines.append(f"| Baseline annual fatalities | {args.baseline_fatalities:,.0f} |")
    lines.append(f"| Baseline annual severe injuries | {args.baseline_severe_injuries:,.0f} |")
    lines.append(f"| Baseline annual minor injuries | {args.baseline_minor_injuries:,.0f} |")
    lines.append(f"| Simulation years | {args.years} |")
    lines.append(f"| Gradual final adoption rate | {args.gradual_final_adoption:.0%} |")
    lines.append(f"| Full adoption rate | {args.full_adoption:.0%} |")
    lines.append(f"| Annual background risk growth | {args.annual_risk_growth:.2%} |")
    lines.append(f"| Accident reduction effectiveness | {args.accident_reduction_effect:.0%} |")
    lines.append(f"| Fatality reduction effectiveness | {args.fatality_reduction_effect:.0%} |")
    lines.append(f"| Severe injury reduction effectiveness | {args.severe_injury_reduction_effect:.0%} |")
    lines.append(f"| Minor injury reduction effectiveness | {args.minor_injury_reduction_effect:.0%} |")
    lines.append(f"| Severity shift factor | {args.severity_shift_factor:.0%} |")
    lines.append(f"| Interaction cap | {args.interaction_cap:.0%} |")
    lines.append("")
    lines.append("## Year-by-Year Results")
    lines.append("")
    lines.append("| Year | No-Adopt Accidents | No-Adopt Fatalities | No-Adopt Severe | No-Adopt Minor | Grad Rate | Grad Accidents | Grad Fatalities | Grad Severe | Grad Minor | Full Rate | Full Accidents | Full Fatalities | Full Severe | Full Minor |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for row in rows:
        lines.append(
            f"| {row.year} "
            f"| {row.no_adoption_accidents:,.0f} "
            f"| {row.no_adoption_fatalities:,.0f} "
            f"| {row.no_adoption_severe_injuries:,.0f} "
            f"| {row.no_adoption_minor_injuries:,.0f} "
            f"| {row.gradual_adoption_rate:.1%} "
            f"| {row.gradual_accidents:,.0f} "
            f"| {row.gradual_fatalities:,.0f} "
            f"| {row.gradual_severe_injuries:,.0f} "
            f"| {row.gradual_minor_injuries:,.0f} "
            f"| {row.full_adoption_rate:.0%} "
            f"| {row.full_accidents:,.0f} "
            f"| {row.full_fatalities:,.0f} "
            f"| {row.full_severe_injuries:,.0f} "
            f"| {row.full_minor_injuries:,.0f} |"
        )
    lines.append("")
    lines.append("## Cumulative Differences")
    lines.append("")
    lines.append("Cumulative totals over all simulated years:")
    lines.append("")
    lines.append("| Scenario | Total Accidents | Total Fatalities | Total Severe Injuries | Total Minor Injuries |")
    lines.append("|---|---|---|---|---|")
    lines.append(f"| No adoption | {cumulative_no.accidents:,.0f} | {cumulative_no.fatalities:,.0f} | {cumulative_no.severe_injuries:,.0f} | {cumulative_no.minor_injuries:,.0f} |")
    lines.append(f"| Gradual adoption | {cumulative_gradual.accidents:,.0f} | {cumulative_gradual.fatalities:,.0f} | {cumulative_gradual.severe_injuries:,.0f} | {cumulative_gradual.minor_injuries:,.0f} |")
    lines.append(f"| Full adoption | {cumulative_full.accidents:,.0f} | {cumulative_full.fatalities:,.0f} | {cumulative_full.severe_injuries:,.0f} | {cumulative_full.minor_injuries:,.0f} |")
    lines.append("")
    lines.append("Illustrative prevented outcomes (no adoption minus scenario):")
    lines.append("")
    lines.append("| Comparison | Prevented Accidents | Prevented Fatalities | Prevented Severe Injuries | Prevented Minor Injuries |")
    lines.append("|---|---|---|---|---|")
    lines.append(f"| No adoption vs gradual adoption | {diff_no_vs_gradual.accidents:,.0f} | {diff_no_vs_gradual.fatalities:,.0f} | {diff_no_vs_gradual.severe_injuries:,.0f} | {diff_no_vs_gradual.minor_injuries:,.0f} |")
    lines.append(f"| No adoption vs full adoption | {diff_no_vs_full.accidents:,.0f} | {diff_no_vs_full.fatalities:,.0f} | {diff_no_vs_full.severe_injuries:,.0f} | {diff_no_vs_full.minor_injuries:,.0f} |")
    lines.append(f"| Gradual adoption vs full adoption | {diff_gradual_vs_full.accidents:,.0f} | {diff_gradual_vs_full.fatalities:,.0f} | {diff_gradual_vs_full.severe_injuries:,.0f} | {diff_gradual_vs_full.minor_injuries:,.0f} |")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("In this illustrative sample, the fatality and severe-injury reduction effect is modeled to be proportionally larger than the total accident reduction.")
    lines.append("This reflects the assumption that speed governance and collision energy reduction act more strongly to prevent fatal and severe-injury outcomes than to prevent all collisions.")
    lines.append("")
    lines.append("Minor injuries may not decrease as sharply as severe injuries, because some prevented severe and fatal outcomes are assumed to shift into minor-injury categories (severity shift factor).")
    lines.append("")
    lines.append("These numbers are not predictions of real-world traffic outcomes.")
    lines.append("They represent a structured comparison of assumptions and should be replaced with validated regional data before any policy or engineering decision.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(MARKDOWN_DISCLAIMER)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Markdown exported: {path}")


def export_summary_json(args: argparse.Namespace, rows: List[YearRow],
                        cumulative_no: Outcome, cumulative_gradual: Outcome,
                        cumulative_full: Outcome, path: str) -> None:
    ensure_dir(path)
    diff_no_vs_gradual = cumulative_no - cumulative_gradual
    diff_no_vs_full = cumulative_no - cumulative_full
    diff_gradual_vs_full = cumulative_gradual - cumulative_full

    summary = {
        "disclaimer": DISCLAIMER,
        "note": "This is an illustrative assumption-based scenario output. Not a certified safety forecast.",
        "assumptions": {
            "baseline_accidents": args.baseline_accidents,
            "baseline_fatalities": args.baseline_fatalities,
            "baseline_severe_injuries": args.baseline_severe_injuries,
            "baseline_minor_injuries": args.baseline_minor_injuries,
            "years": args.years,
            "gradual_final_adoption": args.gradual_final_adoption,
            "full_adoption": args.full_adoption,
            "annual_risk_growth": args.annual_risk_growth,
            "accident_reduction_effect": args.accident_reduction_effect,
            "fatality_reduction_effect": args.fatality_reduction_effect,
            "severe_injury_reduction_effect": args.severe_injury_reduction_effect,
            "minor_injury_reduction_effect": args.minor_injury_reduction_effect,
            "severity_shift_factor": args.severity_shift_factor,
            "interaction_cap": args.interaction_cap,
        },
        "cumulative_totals": {
            "no_adoption": {
                "accidents": round(cumulative_no.accidents, 1),
                "fatalities": round(cumulative_no.fatalities, 1),
                "severe_injuries": round(cumulative_no.severe_injuries, 1),
                "minor_injuries": round(cumulative_no.minor_injuries, 1),
            },
            "gradual_adoption": {
                "accidents": round(cumulative_gradual.accidents, 1),
                "fatalities": round(cumulative_gradual.fatalities, 1),
                "severe_injuries": round(cumulative_gradual.severe_injuries, 1),
                "minor_injuries": round(cumulative_gradual.minor_injuries, 1),
            },
            "full_adoption": {
                "accidents": round(cumulative_full.accidents, 1),
                "fatalities": round(cumulative_full.fatalities, 1),
                "severe_injuries": round(cumulative_full.severe_injuries, 1),
                "minor_injuries": round(cumulative_full.minor_injuries, 1),
            },
        },
        "cumulative_prevented_vs_no_adoption": {
            "gradual_adoption": {
                "accidents": round(diff_no_vs_gradual.accidents, 1),
                "fatalities": round(diff_no_vs_gradual.fatalities, 1),
                "severe_injuries": round(diff_no_vs_gradual.severe_injuries, 1),
                "minor_injuries": round(diff_no_vs_gradual.minor_injuries, 1),
            },
            "full_adoption": {
                "accidents": round(diff_no_vs_full.accidents, 1),
                "fatalities": round(diff_no_vs_full.fatalities, 1),
                "severe_injuries": round(diff_no_vs_full.severe_injuries, 1),
                "minor_injuries": round(diff_no_vs_full.minor_injuries, 1),
            },
        },
        "cumulative_prevented_gradual_vs_full": {
            "accidents": round(diff_gradual_vs_full.accidents, 1),
            "fatalities": round(diff_gradual_vs_full.fatalities, 1),
            "severe_injuries": round(diff_gradual_vs_full.severe_injuries, 1),
            "minor_injuries": round(diff_gradual_vs_full.minor_injuries, 1),
        },
        "final_year_snapshot": {
            "year": rows[-1].year,
            "no_adoption": {
                "accidents": round(rows[-1].no_adoption_accidents, 1),
                "fatalities": round(rows[-1].no_adoption_fatalities, 1),
                "severe_injuries": round(rows[-1].no_adoption_severe_injuries, 1),
                "minor_injuries": round(rows[-1].no_adoption_minor_injuries, 1),
            },
            "gradual_adoption": {
                "rate": round(rows[-1].gradual_adoption_rate, 4),
                "accidents": round(rows[-1].gradual_accidents, 1),
                "fatalities": round(rows[-1].gradual_fatalities, 1),
                "severe_injuries": round(rows[-1].gradual_severe_injuries, 1),
                "minor_injuries": round(rows[-1].gradual_minor_injuries, 1),
            },
            "full_adoption": {
                "rate": round(rows[-1].full_adoption_rate, 4),
                "accidents": round(rows[-1].full_accidents, 1),
                "fatalities": round(rows[-1].full_fatalities, 1),
                "severe_injuries": round(rows[-1].full_severe_injuries, 1),
                "minor_injuries": round(rows[-1].full_minor_injuries, 1),
            },
        },
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Summary JSON exported: {path}")


def run(args: argparse.Namespace) -> List[YearRow]:
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

    rows: List[YearRow] = []
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

        rows.append(YearRow(
            year=year,
            no_adoption_rate=0.0,
            no_adoption_accidents=no_adoption.accidents,
            no_adoption_fatalities=no_adoption.fatalities,
            no_adoption_severe_injuries=no_adoption.severe_injuries,
            no_adoption_minor_injuries=no_adoption.minor_injuries,
            gradual_adoption_rate=gradual_rate,
            gradual_accidents=gradual.accidents,
            gradual_fatalities=gradual.fatalities,
            gradual_severe_injuries=gradual.severe_injuries,
            gradual_minor_injuries=gradual.minor_injuries,
            full_adoption_rate=args.full_adoption,
            full_accidents=full.accidents,
            full_fatalities=full.fatalities,
            full_severe_injuries=full.severe_injuries,
            full_minor_injuries=full.minor_injuries,
        ))

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

    def print_difference(label: str, diff: Outcome) -> None:
        print(
            f"- {label}: "
            f"{format_number(diff.accidents)} accidents, "
            f"{format_number(diff.fatalities)} fatalities, "
            f"{format_number(diff.severe_injuries)} severe injuries, "
            f"{format_number(diff.minor_injuries)} minor injuries"
        )

    print_difference("No adoption minus gradual adoption", cumulative_no - cumulative_gradual)
    print_difference("No adoption minus full adoption", cumulative_no - cumulative_full)
    print_difference("Gradual adoption minus full adoption", cumulative_gradual - cumulative_full)
    print()
    print(DISCLAIMER)

    if args.output_csv:
        export_csv(rows, args.output_csv)
    if args.output_markdown:
        export_markdown(rows, args, cumulative_no, cumulative_gradual, cumulative_full, args.output_markdown)
    if args.output_summary_json:
        export_summary_json(args, rows, cumulative_no, cumulative_gradual, cumulative_full, args.output_summary_json)

    return rows


def main() -> None:
    parser = build_parser()
    run(parser.parse_args())


if __name__ == "__main__":
    main()

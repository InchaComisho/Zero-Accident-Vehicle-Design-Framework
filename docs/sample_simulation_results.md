# Sample Simulation Results

> **Disclaimer:** This page shows illustrative assumption-based sample outputs from the adoption scenario comparison model.
> The numbers shown here do not predict real-world traffic accident counts.
> They are conceptual outputs for comparing no adoption, gradual adoption, and full adoption under explicit assumptions.
> This is not a certified safety forecast.
> It does not guarantee accident, fatality, or severe-injury reduction.
> Real-world outcomes depend on baseline traffic data, adoption rates, road design, driver behavior, weather, vehicle fleet composition, regulation, infrastructure quality, and sensor reliability.
> Real-world validation is required before any safety claim can be made.

---

## Assumptions

The following illustrative assumptions were used to generate these sample outputs.
These are not empirical values and must be replaced with validated regional data before any policy or engineering decision.

| Parameter | Value |
|---|---|
| Baseline annual accidents | 100,000 |
| Baseline annual fatalities | 1,000 |
| Baseline annual severe injuries | 5,000 |
| Baseline annual minor injuries | 30,000 |
| Simulation years | 20 |
| Gradual final adoption rate | 80% |
| Full adoption rate | 100% |
| Annual background risk growth | 0.00% |
| Accident reduction effectiveness | 35% |
| Fatality reduction effectiveness | 80% |
| Severe injury reduction effectiveness | 70% |
| Minor injury reduction effectiveness | 20% |
| Severity shift factor | 30% |
| Interaction cap | 90% |

---

## Key Findings

These findings are illustrative, not predictions.

In this sample, the fatality and severe-injury reduction effect is modeled to be proportionally larger than the total accident reduction.
This reflects the assumption that speed governance and collision energy reduction act more strongly to prevent fatal and severe-injury outcomes than to prevent all collisions.

**Year 20 annual snapshot (illustrative):**

| Scenario | Accidents | Fatalities | Severe Injuries | Minor Injuries |
|---|---|---|---|---|
| No adoption | 100,000 | 1,000 | 5,000 | 30,000 |
| Gradual adoption (80% reached) | 72,000 | 360 | 2,200 | 26,232 |
| Full adoption (100%) | 65,000 | 200 | 1,500 | 25,290 |

**Cumulative illustrative differences over 20 years:**

| Comparison | Prevented Accidents | Prevented Fatalities | Prevented Severe Injuries |
|---|---|---|---|
| No adoption vs gradual adoption | 280,000 | 6,400 | 28,000 |
| No adoption vs full adoption | 700,000 | 16,000 | 70,000 |

---

## Graphs

The graphs below are illustrative assumption-based outputs.
They are not certified safety forecasts.

![Illustrative fatalities scenario](../images/adoption_scenario_fatalities.png)

![Illustrative severe injuries scenario](../images/adoption_scenario_severe_injuries.png)

![Illustrative total accidents scenario](../images/adoption_scenario_total_accidents.png)

![Illustrative cumulative prevented outcomes](../images/adoption_scenario_cumulative_prevented.png)

---

## Sample Result Files

- [Sample results table](../results/adoption_scenario_sample_results.md)
- [Sample results CSV](../results/adoption_scenario_sample_results.csv)
- [Sample summary JSON](../results/adoption_scenario_sample_summary.json)

---

## Interpretation

In this illustrative sample, total accidents decrease less sharply than fatalities or severe injuries.
This reflects the modeling choice that speed governance and impact energy reduction are more effective at preventing the worst outcomes than at preventing every collision.

Minor injuries may not decrease as sharply as severe injuries because some prevented severe and fatal outcomes are assumed to shift into minor-injury categories under the severity shift factor.

These numbers are structured comparisons of assumptions, not predictions of real traffic outcomes.

---

## Limitations

This model does not prove that zero accidents, zero fatalities, or zero severe injuries are achievable.

Actual outcomes depend on:

- local traffic laws and enforcement
- baseline accident, fatality, and injury rates
- road design and infrastructure quality
- driver behavior and social acceptance
- weather and environmental conditions
- vehicle fleet composition and maintenance quality
- sensor reliability and cybersecurity
- privacy regulation
- emergency response quality

Any practical use of this framework requires empirical traffic data, controlled trials, regional validation, legal review, cybersecurity assessment, privacy assessment, and formal safety engineering.

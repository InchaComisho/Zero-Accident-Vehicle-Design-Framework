# Simulations

This directory contains simple conceptual simulation tools for the Zero-Accident Vehicle Design Framework.

## Adoption Scenario Simulator

The adoption scenario simulator compares no adoption, gradual adoption, and full adoption pathways for the Zero-Accident Vehicle Design Framework.

It is a severity-aware illustrative model. It separates total accidents, fatalities, severe injuries, and minor injuries because safety systems may reduce severe outcomes more strongly than total crash occurrence.

It is not a real-world safety forecast and does not guarantee reductions.

Example:

```bash
python simulations/adoption_scenario_simulator.py --baseline-accidents 100000 --baseline-fatalities 1000 --baseline-severe-injuries 5000 --baseline-minor-injuries 30000 --years 20
```

Another example:

```bash
python simulations/adoption_scenario_simulator.py --baseline-accidents 50000 --baseline-fatalities 300 --baseline-severe-injuries 1500 --baseline-minor-injuries 12000 --years 15 --gradual-final-adoption 0.6 --interaction-cap 0.85
```

Export results to files:

```bash
python simulations/adoption_scenario_simulator.py \
  --baseline-accidents 100000 \
  --baseline-fatalities 1000 \
  --baseline-severe-injuries 5000 \
  --baseline-minor-injuries 30000 \
  --years 20 \
  --output-csv results/adoption_scenario_sample_results.csv \
  --output-markdown results/adoption_scenario_sample_results.md \
  --output-summary-json results/adoption_scenario_sample_summary.json
```

Generate graphs:

```bash
python simulations/generate_sample_graphs.py
```

## Generated sample outputs

The repository includes committed sample outputs so readers can see results without running the simulator locally:

- `results/adoption_scenario_sample_results.csv`
- `results/adoption_scenario_sample_results.md`
- `results/adoption_scenario_sample_summary.json`
- `images/adoption_scenario_fatalities.png`
- `images/adoption_scenario_severe_injuries.png`
- `images/adoption_scenario_total_accidents.png`
- `images/adoption_scenario_cumulative_prevented.png`

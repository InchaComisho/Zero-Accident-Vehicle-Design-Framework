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

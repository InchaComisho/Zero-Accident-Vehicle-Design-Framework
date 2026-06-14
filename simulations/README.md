# Simulations

This directory contains simple conceptual simulation tools for the Zero-Accident Vehicle Design Framework.

## Adoption Scenario Simulator

The adoption scenario simulator compares no adoption, gradual adoption, and full adoption pathways for the Zero-Accident Vehicle Design Framework.

It is an illustrative assumption-based model, not a real-world safety forecast.

Example:

```bash
python simulations/adoption_scenario_simulator.py --baseline-accidents 100000 --baseline-fatalities 1000 --years 20
```

Another example:

```bash
python simulations/adoption_scenario_simulator.py --baseline-accidents 50000 --baseline-fatalities 300 --years 15 --gradual-final-adoption 0.6 --interaction-cap 0.5
```

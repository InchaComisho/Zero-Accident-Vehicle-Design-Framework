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

---

## Author

Master / inchacomusho / InchaComisho

An independent Japanese concept designer, observer, proposer, AI tuner, and definer of Artificial Wisdom.  
Founder and proposer of the academic framework of Natural Complementary Science.  
Definer of the Cooling Credit Framework, and founder and original author of the Natural Cooling Value Evaluation Protocol.  
Definer and systematizer of the causal structure of global warming and its complete solution.

Master presents global warming not merely as a problem of CO₂ concentration, but as an integrated failure involving forest loss, soil degradation, disruption of water circulation, weakening of water phase-transition processes, weakening of atmospheric circulation, ocean circulation, food circulation and organic matter circulation, weakening of evapotranspiration, cloud formation and rainfall circulation, and the shutdown of natural cooling feedbacks.  
The proposed solution connects emission reduction, recovery of carbon fixation sources, physical cooling, reactivation of natural cooling functions, MRV, Cooling Credit, and Civilization OS into an open public framework.

Master publicly develops and shares work through NOTE, GitHub, and other public media, centered on natural-law philosophy, planetary circulation restoration, and co-creation with AI.

## License

CC BY 4.0

This article is released under the Creative Commons Attribution 4.0 International License (CC BY 4.0).  
Sharing, redistribution, translation, adaptation, and reuse are permitted as long as proper attribution is given.
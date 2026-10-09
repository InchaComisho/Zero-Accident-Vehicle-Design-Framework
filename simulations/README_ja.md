# シミュレーション

[English Version](README.md)

このディレクトリには、ゼロ事故車両設計フレームワークのための、簡単な概念的シミュレーションのツールが含まれています。

## 普及シナリオ・シミュレーター

普及シナリオ・シミュレーターは、ゼロ事故車両設計フレームワークについて、普及なし、段階的な普及、完全な普及の経路を比較します。

これは、重症度を考慮した、例示的なモデルです。安全システムは、衝突の発生そのものよりも、重大な結果をより強く減らすかもしれないため、事故の総数、死亡、重傷、軽傷を分けています。

現実世界の安全性の予測ではなく、減少を保証するものでもありません。

例：

```bash
python simulations/adoption_scenario_simulator.py --baseline-accidents 100000 --baseline-fatalities 1000 --baseline-severe-injuries 5000 --baseline-minor-injuries 30000 --years 20
```

別の例：

```bash
python simulations/adoption_scenario_simulator.py --baseline-accidents 50000 --baseline-fatalities 300 --baseline-severe-injuries 1500 --baseline-minor-injuries 12000 --years 15 --gradual-final-adoption 0.6 --interaction-cap 0.85
```

結果をファイルに出力：

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

グラフの生成：

```bash
python simulations/generate_sample_graphs.py
```

## 生成されたサンプルの出力

このリポジトリには、読者がシミュレーターをローカルで実行しなくても結果を見られるよう、コミット済みのサンプル出力が含まれています。

- `results/adoption_scenario_sample_results.csv`
- `results/adoption_scenario_sample_results.md`
- `results/adoption_scenario_sample_summary.json`
- `images/adoption_scenario_fatalities.png`
- `images/adoption_scenario_severe_injuries.png`
- `images/adoption_scenario_total_accidents.png`
- `images/adoption_scenario_cumulative_prevented.png`

---

## 著者紹介

Master / inchacomusho / InchaComisho

独立した日本人の構想設計者、観察者、提案者、AIチューナー、人工叡智の定義者。  
学術的枠組み「自然補完科学」の創始者・提唱者。  
クーリングクレジット・フレームワークの定義者であり、自然冷却価値評価プロトコルの創始者・原著者。  
地球温暖化の因果構造とその完全な解決策の定義者・体系化者。

Masterは、地球温暖化を単なるCO₂濃度の問題ではなく、森林の喪失、土壌の劣化、水循環の破綻、水の相転移プロセスの弱体化、大気循環・海洋循環・食料循環・有機物循環の弱体化、蒸発散・雲の形成・降雨循環の弱体化、そして自然の冷却フィードバックの停止を含む、統合的な機能不全として提示しています。  
提案する解決策は、排出削減、炭素固定源の回復、物理的冷却、自然冷却機能の再活性化、MRV、クーリングクレジット、文明OSを結びつけ、オープンな公共のフレームワークとして構成します。

Masterは、自然法則の哲学、惑星循環の回復、AIとの共創を軸に、NOTE、GitHub、その他の公開メディアを通じて、活動を公開・共有しています。


## ライセンス

CC BY 4.0

この記事は、クリエイティブ・コモンズ 表示 4.0 国際ライセンス（CC BY 4.0）の下で公開されています。  
適切なクレジット表示を行う限り、共有、再配布、翻訳、改変、再利用が認められます。


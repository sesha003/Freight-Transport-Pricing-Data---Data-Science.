# FreightIQ — Data-Driven Freight Price Prediction

**A Machine Learning Approach to Transport Cost Optimisation in India**

Hochschule Furtwangen University · M.Sc. Data Science & AI for Digital Business Management
AIM — Data Science & AI Business Project

---

## Overview

Freight pricing in Indian road logistics is opaque. Rates are negotiated per lane, vary by vehicle and contract type, and don't scale linearly with distance — which makes budgeting and rate negotiation largely reactive.

FreightIQ turns four years of historical shipment records into a predictive pricing engine. Given a route, vehicle, product and load, the model estimates the expected freight cost, explains *why* it arrived at that number, and forecasts costs weeks ahead for planning.

The project follows a CRISP-DM structure: business understanding → data cleaning → EDA → modelling → evaluation → business deployment.

---

## Dataset

| | |
|---|---|
| **Raw records** | 423,311 shipments |
| **Raw columns** | 21 (numerical, categorical, temporal) |
| **Period** | FY 2022 – 2025 |
| **After cleaning & dedup** | 386,072 shipments |
| **Modelling features** | 13–14 |

**Feature groups**

| Group | Columns | Why it matters |
|---|---|---|
| Route geography | Source, Source State, Destination, Destination State | Lane-specific supply and demand |
| Operational | Contract type, Product, Pricing type, Vehicle type, Body type | Pricing structure and cargo handling |
| Commercial | Distance, Vehicle Load | Direct driver of fuel, time and toll cost |
| Temporal | Year, Month, Week | Seasonal and year-on-year pricing patterns |

`Price_per_KM` was deliberately **excluded** — it equals Cost ÷ Distance and would leak the target into the model.

---

## Models

Five algorithms were trained on the same cleaned dataset, each with a baseline and a tuned configuration. Selection was **validation-first**: baseline vs. tuned was decided on validation metrics only, and the test set was consulted once for the final honest score.

### Regression — predicting freight cost in ₹

| Model | Test R² | MAE (₹) | RMSE (₹) | MAPE |
|---|---|---|---|---|
| **XGBoost (tuned)** ⭐ | **0.9705** | **124.60** | **241.43** | **9.69%** |
| Random Forest (baseline) | 0.9662 | 111.06 | 257.61 | 10.94% |
| Gradient Boosting (tuned) | 0.9581 | 172.16 | 286.90 | 13.14% |
| Decision Tree (tuned) | 0.9325 | 178.35 | 365.23 | ~13.5% |

**XGBoost is the final model** — it wins on R², RMSE and MAPE, with tuning cutting its MAE by roughly 50%.

Notable behaviours:
- **Gradient Boosting** gained the most from tuning (R² 0.80 → 0.96) via deeper trees, more boosting stages, and validation-based early stopping.
- **Random Forest** was strong out of the box; regularising the tuned variant actually *increased* validation MAE, so the baseline was kept — a useful negative result.
- **Decision Tree** tuning barely moved accuracy but halved the overfitting gap (0.0727 → 0.0346).

### Classification — predicting cost tier (Low / Medium / High)

Multinomial **Logistic Regression** was included as a transparent, interpretable baseline for tier prediction rather than an exact rupee amount.

| Tier | ROC-AUC |
|---|---|
| Low | 0.956 |
| Medium | 0.885 |
| High | 0.956 |

Low and High separate cleanly; Medium is harder to isolate because it borders both neighbouring tiers on the cost spectrum. Almost all errors are adjacent-tier mix-ups — the expected ordinal failure mode.

---

## Explainability (XAI)

Every model was audited with multiple independent importance methods so the ranking isn't an artifact of any one technique:

- **MDI** (impurity-based feature importance)
- **Permutation importance** (measured on held-out data)
- **SHAP** — global beeswarm plots plus per-shipment waterfall explanations

All three converge on the same story:

**Distance dominates** (63–66% importance across tree models), followed by **source city and source state**, then destination geography, vehicle load and product. `Pricing_Type` contributes ≈0% in the cleaned data and is retained only for feature-set consistency across the team.

SHAP waterfalls make individual predictions defensible to a business audience — e.g. a ₹4,139 prediction decomposes into a ₹2,742 baseline plus +₹620 for long distance, +₹273 for a high-cost origin city, and so on. That's the difference between "the model says ₹4,139" and "this lane is expensive *because* it's long and originates in a high-rate city."

---

## Business Impact

A **Looker Studio dashboard** presents historical prices (2022–2025) alongside predicted prices for April 2026, filterable by source, destination, vehicle type, body type, contract type and week.

What it enables:
- **Proactive budgeting** — freight cost forecast weeks ahead, per route
- **Stronger negotiation** — data-backed rate benchmarks across four years
- **Smarter choices** — cost drivers surfaced by route and vehicle type
- **Fewer surprises** — historical vs. predicted cost, side by side

With an average error under ₹125 (~4.5% of the ₹2,740 mean shipment cost), the model is accurate enough for operational pricing, budgeting and freight planning decisions.

---

## Tech Stack

`Python` · `pandas` · `NumPy` · `scikit-learn` · `XGBoost` · `SHAP` · `Matplotlib` · `Seaborn` · `Jupyter` · `Looker Studio`

---

## My Contribution

**Data cleaning — Source city & Source State.** The raw dataset carried inconsistent, misspelt and mismatched origin fields (mixed casing, city/state disagreements, non-standard spellings of Indian place names). I cleaned and standardised these into the `Corrected_Source` and `Corrected_Source_State` columns used by **every** model in this project. This mattered more than expected: source city and source state land second and third in feature importance behind distance, so the reliability of that geography signal directly bounds the accuracy of all five models.

**Gradient Boosting model.** I built the full Gradient Boosting regression pipeline end to end:
- Label encoding with a persisted `encoding_mapping`, so unseen April routes are encoded exactly as in training
- 80/10/10 train/validation/test split with fixed `random_state=42` for reproducibility
- Baseline model (100 stages, depth 3) → tuned model (500 stages, depth 8, subsample 0.8)
- **Validation-based early stopping** using `staged_predict` — scoring the ensemble after every boosting stage and keeping the stage with the highest validation R², so trees that would only overfit are never added
- Validation-first model selection, lifting R² from 0.8020 → **0.9581** on test while keeping the train–test gap at just 0.0135
- Error analysis, MDI + permutation importance, SHAP explainability, and high-cost shipment detection (F1 0.901, ROC-AUC 0.990)

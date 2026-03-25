# Restaurant Feasibility Diagnostic Model

This project converts the Excel feasibility workbook into a structured Python model for the capstone topic:
"Why My Restaurant Isn't Working? A Diagnostic Framework for F&B Success in Ahmedabad".

## What the model does

- Calculates a weighted demand score using the same factors and weights from the Excel model.
- Projects customer volume, monthly revenue, scenario revenue, and 3-year revenue.
- Benchmarks monthly costs against expected restaurant cost ratios.
- Computes profitability, payback period, and a viability verdict.
- Generates a success probability, risk score, and strategic recommendations.

## Project structure

- `restaurant_model/schemas.py`: input schema and validation
- `restaurant_model/engine.py`: diagnostic logic
- `main.py`: example runner
- `streamlit_app.py`: interactive dashboard
- `sample_input.json`: sample restaurant profile based on the Excel workbook

## How to run

Use any Python 3.10+ interpreter:

```bash
python main.py
```

To launch the dashboard:

```bash
streamlit run streamlit_app.py
```

## Model design

This is a rule-based diagnostic model, not a trained machine-learning classifier. That is a good fit for the current capstone stage because:

- your proposal focuses on a practical diagnostic framework
- the Excel workbook already defines business logic and benchmarks
- primary research can later be used to calibrate the success-probability formula

## Suggested next capstone step

Once you collect more owner and customer data, you can upgrade this into a data-driven predictive model by:

1. storing restaurants as rows in a dataset
2. labeling outcomes as successful / struggling / failed
3. training a classifier such as logistic regression, random forest, or XGBoost
4. comparing predicted success probability with this rule-based baseline

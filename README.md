# Assured Contract Farming System

A starter implementation of an Assured Contract Farming System combining:

- Farmer and buyer workflows
- Digital contract management
- Agricultural market price prediction
- Buyer-farmer matching
- Price-based decision support

## Current ML implementation

The model uses a Random Forest Regressor to predict `Modal Price` from agricultural market features.

### ML workflow

Dataset -> preprocessing -> train/test split -> one-hot encoding -> Random Forest -> prediction -> MAE/RMSE/R2 evaluation

## Project structure

```text
assured-contract-farming-system/
├── backend/
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       └── style.css
├── data/
│   └── cleaned_agriculture_data.csv
├── database/
├── frontend/
├── ml/
│   └── train_model.py
├── model/
│   └── .gitkeep
├── docs/
├── requirements.txt
└── .gitignore
```

## Run the ML model

```bash
pip install -r requirements.txt
python ml/train_model.py
```

The trained model is saved under `model/`.

## Run the Flask backend

```bash
python backend/app.py
```

Then open:

http://127.0.0.1:5000

## Important note

The current Random Forest experiment predicts the modal price using same-record market features such as minimum and maximum price. This is a useful baseline, but it should not be described as true future forecasting until lagged historical features are used.

Also, the original report mentions Decision Tree and Linear Regression in different sections. This implementation intentionally uses Random Forest because that is the model selected for the current experiment.

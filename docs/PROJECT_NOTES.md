# Project Notes

## Main system idea

The system connects farmers and buyers through digital assured contracts while
using agricultural market data for price-related decision support.

## Main modules

1. Farmer module
2. Buyer module
3. Contract module
4. Price prediction module
5. Matching module
6. Admin module

## Current model

Random Forest Regressor.

Target:
- Modal Price

Categorical inputs:
- State
- District
- Market
- Commodity
- Variety
- Grade
- Season

Numerical inputs:
- Min Price
- Max Price
- Year
- Month
- Day
- DayOfWeek
- Quarter

## Model limitation

Using same-record Min Price and Max Price to predict same-record Modal Price
can create a model that performs well as a regression baseline but does not
represent genuine future price forecasting. For a true forecasting system,
future-safe lag features should be created from previous market observations.

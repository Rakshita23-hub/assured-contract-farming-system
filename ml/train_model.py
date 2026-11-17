from pathlib import Path
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "updated_agriculture_data.csv"
MODEL_PATH = BASE_DIR / "model" / "random_forest_price_model.pkl"


# 1. Load dataset
print("Loading dataset...")

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully!")
print("Shape:", df.shape)


# 2. Remove unnecessary column if present
if "price_range_inconsistent" in df.columns:
    df = df.drop(columns=["price_range_inconsistent"])


# 3. Define features
features = [
    "State",
    "District",
    "Market",
    "Commodity",
    "Variety",
    "Grade",
    "Min Price",
    "Max Price",
    "Year",
    "Month",
    "Day",
    "DayOfWeek",
    "Quarter",
    "Season"
]

target = "Modal Price"


# 4. Separate input and target
X = df[features]
y = df[target]


# 5. Define categorical features
categorical_features = [
    "State",
    "District",
    "Market",
    "Commodity",
    "Variety",
    "Grade",
    "Season"
]


# 6. Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("Training data:", X_train.shape)
print("Testing data:", X_test.shape)


# 7. Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        )
    ],
    remainder="passthrough"
)


# 8. Random Forest model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)


# 9. Create pipeline
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", model)
])


# 10. Train model
print("\nTraining Random Forest model...")

pipeline.fit(X_train, y_train)

print("Model trained successfully!")


# 11. Prediction
print("\nMaking predictions...")

y_pred = pipeline.predict(X_test)


# 12. Evaluation
mae = mean_absolute_error(y_test, y_pred)

rmse = mean_squared_error(
    y_test,
    y_pred
) ** 0.5

r2 = r2_score(y_test, y_pred)


print("\n==============================")
print("MODEL EVALUATION")
print("==============================")

print("MAE :", mae)
print("RMSE:", rmse)
print("R2  :", r2)


# 13. Save model
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

joblib.dump(pipeline, MODEL_PATH)

print("\nModel saved successfully!")
print("Location:", MODEL_PATH)
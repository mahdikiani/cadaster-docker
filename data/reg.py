import lightgbm as lgb
import numpy as np
import pandas as pd
import tabulate
import xgboost as xgb
from catboost import CatBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge
from sklearn.metrics import make_scorer, mean_squared_error
from sklearn.model_selection import KFold, cross_val_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor

# Example data
data = {
    "x": [3847, 3632, 3430, 3381, 2768, 740, 522, 876, 745, 943],
    "y": [1381, 1366, 759, 540, 450, 125, 501, 1606, 2050, 2370],
    "Lat": [
        38.43891667,
        38.45548889,
        39.10249167,
        39.33685278,
        39.43357778,
        39.77645278,
        39.38044444,
        38.19739167,
        37.71528889,
        37.36770833,
    ],
    "Lng": [
        48.87637222,
        48.58227222,
        48.30448056,
        48.23882222,
        47.39654167,
        44.60801111,
        44.31150833,
        44.79651667,
        44.617175,
        44.88973889,
    ],
}
data = pd.DataFrame(data)
data = pd.read_csv("map.csv")

# Models
models = (
    {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(),
        "DTree": DecisionTreeRegressor(),
        "Gradient Boosting": GradientBoostingRegressor(),
        "SVR": SVR(),
        "KNN": KNeighborsRegressor(),
        "MLP": MLPRegressor(),
        "CatBoost": CatBoostRegressor(),
        "LightGBM": lgb.LGBMRegressor(),
        "XGBoost": xgb.XGBRegressor(),
    }
    # | {f"Ridge ({alpha})": Ridge(alpha=alpha) for alpha in np.arange(0.1, 1.1, 0.1)}
    # | {f"Lasso ({alpha})": Lasso(alpha=alpha) for alpha in np.arange(0.1, 1.1, 0.1)}
)

# System 1: Predict (Lat, Lng) from (x, y)
X1 = data[["x", "y"]]
y11 = data["Lat"]
y12 = data["Lng"]

# System 2: Predict (x, y) from (Lat, Lng)
X2 = data[["Lat", "Lng"]]
y21 = data["x"]
y22 = data["y"]

# 5-Fold Cross-Validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Custom scorer: Mean Squared Error
mse_scorer = make_scorer(mean_squared_error, greater_is_better=False)

result = []
# Training and Evaluation
for name, model in models.items():
    # System 1
    mse11 = -cross_val_score(model, X1, y11, cv=kf, scoring=mse_scorer).mean()
    mse12 = -cross_val_score(model, X1, y12, cv=kf, scoring=mse_scorer).mean()

    # System 2
    mse21 = -cross_val_score(model, X2, y21, cv=kf, scoring=mse_scorer).mean()
    mse22 = -cross_val_score(model, X2, y22, cv=kf, scoring=mse_scorer).mean()

    result.append([name, mse11, mse12, mse21, mse22])

    print(
        "\n".join(
            [
                f"{name}",
                f"System 11 Avg MSE: {mse11}",
                f"System 12 Avg MSE: {mse12}",
                f"System 21 Avg MSE: {mse21}",
                f"System 22 Avg MSE: {mse22}",
                "",
            ]
        )
    )

result = pd.DataFrame(
    result, columns=["Model", "System 11", "System 12", "System 21", "System 22"]
)
result.to_csv("result.csv", index=False)
print(tabulate.tabulate(result, headers="keys", tablefmt="psql"))

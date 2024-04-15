import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

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

data = pd.DataFrame(data)
data = pd.read_csv("map.csv")

# Split into train/test sets
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

# System 1: Predict (Lat, Lng) from (x, y)
X1 = train_data[["x", "y"]]
y1 = train_data[["Lat", "Lng"]]

# Train Linear Regression model for System 1
model1 = LinearRegression().fit(X1, y1)

# System 2: Predict (x, y) from (Lat, Lng)
X2 = train_data[["Lat", "Lng"]]
y2 = train_data[["x", "y"]]

# Train Linear Regression model for System 2
model2 = LinearRegression().fit(X2, y2)


# Define a function to use the trained models
def predict_coordinates(input_coords, input_type="xy"):
    """
    Predict coordinates using trained Linear Regression models.

    Parameters:
        input_coords (tuple): Input coordinates.
        input_type (str): Type of the input coordinates ('xy' or 'latlng').

    Returns:
        tuple: Predicted coordinates.
    """
    input_data = pd.DataFrame([input_coords])

    if input_type == "xy":
        predictions = model1.predict(input_data)
        return predictions[0][0], predictions[0][1]  # Lat, Lng
    elif input_type == "latlng":
        predictions = model2.predict(input_data)
        return predictions[0][0], predictions[0][1]  # x, y
    else:
        raise ValueError("Invalid input_type. Choose 'xy' or 'latlng'.")


def dec_to_deg(dec):
    deg = int(dec)
    min = int((dec - deg) * 60)
    sec = (dec - deg - min / 60) * 3600
    return deg, min, sec


# Example usage
input_coords = (3277, 5125)  # Example coordinates
predicted_latlng = predict_coordinates(input_coords, input_type="xy")
predicted_latlng_degree = dec_to_deg(predicted_latlng[0]), dec_to_deg(
    predicted_latlng[1]
)
print(
    "\n".join(
        [
            f"Input (x, y): {input_coords}",
            f"Predicted (Lat, Lng): {predicted_latlng}",
            f"Predicted (Lat, Lng): {predicted_latlng_degree}",
        ]
    )
)

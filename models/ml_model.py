import numpy as np
from sklearn.ensemble import RandomForestClassifier

# -----------------------------
# Transform features to risk direction
# -----------------------------

def transform(mood, stress, sleep):
    mood_risk = 6 - mood      # lower mood = higher risk
    sleep_risk = 6 - sleep    # poor sleep = higher risk
    return [mood_risk, stress, sleep_risk]


# Strong synthetic dataset
X_raw = [
    # High depression risk
    [1,5,1],
    [1,5,2],
    [2,5,1],
    [1,4,1],
    [2,4,2],
    [1,5,1],
    [2,5,2],

    # Medium risk
    [3,4,2],
    [2,3,3],
    [3,3,2],
    [3,4,3],

    # Low risk
    [5,1,5],
    [4,2,4],
    [5,2,5],
    [4,1,4],
    [5,1,4],
    [4,2,5],
]

X = np.array([transform(m,s,l) for m,s,l in X_raw])

y = np.array([
    1,1,1,1,1,1,1,
    1,1,1,1,
    0,0,0,0,0,0
])

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)


def predict_depression(mood, stress, sleep):
    input_data = np.array([transform(mood, stress, sleep)])
    probability = model.predict_proba(input_data)[0][1]
    return probability
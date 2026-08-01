import numpy as np
from sklearn.ensemble import IsolationForest

model = IsolationForest(contamination=0.1, random_state=42)

def train_model():
    normal_data = np.random.uniform(40.0, 50.0, (500, 1))
    model.fit(normal_data)
    print(f"[ML] Model trained on {len(normal_data)} normal samples")

def predict(value):
    prediction = model.predict([[value]])
    return prediction[0]

train_model()

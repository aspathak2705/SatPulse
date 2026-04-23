from sklearn.ensemble import IsolationForest

def train_isolation_forest(data):
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(data)
    return model


def predict_isolation_forest(model, data):
    preds = model.predict(data)
    return preds  # -1 = anomaly, 1 = normal
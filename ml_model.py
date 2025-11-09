# ml_model.py
import os
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

class MLModel:
    def __init__(self):
        self.model_path = "xgb_model.json"
        self.model = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
        if os.path.exists(self.model_path):
            self.model.load_model(self.model_path)
        else:
            X = np.random.randn(500, 3)
            y = np.random.choice([0,1,2], size=500)
            self.model.fit(X, y)
            self.model.save_model(self.model_path)

    def predict(self, closes, signals):
        feat = np.array(signals).reshape(1, -1)
        pred = self.model.predict(feat)[0]
        return {0: 0, 1: 1, 2: -1}.get(pred, 0)

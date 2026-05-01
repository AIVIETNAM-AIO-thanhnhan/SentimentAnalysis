| Metric             | Target     | Priority |
|--------------------|------------|----------|
| Accuracy           | ≥ 80%      | Medium   |
| Macro F1           | ≥ 0.78     | High     |
| Neutral class F1   | ≥ 0.65     | High     |
| API latency        | ≤ 200ms    | Medium   |

Here's how to calculate macro F1 score in scikit-learn — it's just a few lines once your model has made predictions.
The key parameter is average='macro', which treats all three classes (Positive, Neutral, Negative) equally regardless of how many samples each has. This is what you want for sentiment analysis since you care about getting all three classes right, not just the majority one.

```
from sklearn.metrics import f1_score, classification_report
import joblib
import pandas as pd

# Load your saved model and vectorizer
model = joblib.load('models/model.pkl')
vectorizer = joblib.load('models/vectorizer.pkl')

# Load test set
test = pd.read_csv('data/test.csv')
X_test = vectorizer.transform(test['clean_text'])
y_true = test['label']

# Get predictions
y_pred = model.predict(X_test)

# ── Macro F1 (your main metric) ──────────────────────────────
macro_f1 = f1_score(y_true, y_pred, average='macro')
print(f"Macro F1: {macro_f1:.4f}")

# ── Full breakdown (the most useful output) ───────────────────
print(classification_report(y_true, y_pred,
      target_names=['negative', 'neutral', 'positive']))
```

The classification_report output will look like this:

                   precision   recall    f1-score   support

    negative         0.88      0.91      0.89        80
     neutral         0.74      0.70      0.72        60
    positive         0.90      0.88      0.89       110

    accuracy                             0.86       250
    macro avg        0.84      0.83      0.83       250
    weighted avg     0.86      0.86      0.86       250

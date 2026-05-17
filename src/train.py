"""
train.py — Train Vietnamese Sentiment Model
============================================
Cách chạy:
    python notebook/train.py

Output:
    models/sentiment_model.joblib
    models/results.png
"""

import os, warnings
import pandas as pd
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (classification_report, confusion_matrix,
                              accuracy_score, f1_score)
from scipy.sparse import hstack
import joblib
warnings.filterwarnings('ignore')

# ── Paths ─────────────────────────────────────────────────────────
BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE, "data",   "cleaned_data.csv")
MDL_DIR   = os.path.join(BASE, "models")
MDL_PATH  = os.path.join(MDL_DIR, "sentiment_model.joblib")
REPORT_DIR   = os.path.join(BASE, "reports")
PLOT_PATH = os.path.join(REPORT_DIR, "model_test_results.png")
os.makedirs(MDL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# ── 1. Load & clean ───────────────────────────────────────────────
print("📂 Loading data...")
df = pd.read_csv(DATA_PATH)
df.dropna(subset=['clean_comment', 'sentiment'], inplace=True)
df['clean_comment'] = df['clean_comment'].astype(str).str.strip()
df = df[df['clean_comment'].str.len() > 1]
print(f"   Samples : {len(df):,}")
print(f"   Labels  : {df['sentiment'].value_counts().to_dict()}\n")

X = df['clean_comment']
y = df['sentiment']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

# ── 2. TF-IDF (word + char n-gram) ───────────────────────────────
print("🔧 Building TF-IDF features...")
tfidf_word = TfidfVectorizer(analyzer='word', ngram_range=(1,3),
    max_features=50000, sublinear_tf=True, min_df=2, max_df=0.95)
tfidf_char = TfidfVectorizer(analyzer='char_wb', ngram_range=(3,5),
    max_features=30000, sublinear_tf=True, min_df=3)

Xtr = hstack([tfidf_word.fit_transform(X_train),
               tfidf_char.fit_transform(X_train)])
Xte = hstack([tfidf_word.transform(X_test),
               tfidf_char.transform(X_test)])
Xtr_w = tfidf_word.transform(X_train)   # for NB
Xte_w = tfidf_word.transform(X_test)
print(f"   Feature dims: {Xtr.shape}\n")

# ── 3. Train & evaluate ───────────────────────────────────────────
print("🤖 Training models...")
MODELS = {
    'Logistic Regression': (
        LogisticRegression(C=5.0, max_iter=1000, solver='saga',
                           class_weight='balanced', random_state=42), True),
    'LinearSVC': (
        LinearSVC(C=1.0, max_iter=2000,
                  class_weight='balanced', random_state=42), True),
    'Naive Bayes': (MultinomialNB(alpha=0.1), False),
}

results = {}
for name, (clf, use_char) in MODELS.items():
    clf.fit(Xtr if use_char else Xtr_w, y_train)
    pred = clf.predict(Xte if use_char else Xte_w)
    acc  = accuracy_score(y_test, pred)
    f1   = f1_score(y_test, pred, average='macro')
    results[name] = dict(clf=clf, pred=pred, acc=acc, f1=f1, use_char=use_char)
    print(f"   [{name:22s}]  Accuracy={acc:.4f}  Macro-F1={f1:.4f}")

# ── 4. Best model ─────────────────────────────────────────────────
best = max(results, key=lambda k: results[k]['f1'])
r    = results[best]
print(f"\n{'='*52}")
print(f"✅ Best model : {best}")
print(f"   Accuracy  : {r['acc']:.4f}")
print(f"   Macro-F1  : {r['f1']:.4f}")
print('='*52)
print(classification_report(y_test, r['pred'],
      target_names=['NEGATIVE','NEUTRAL','POSITIVE']))

# ── 5. Save ───────────────────────────────────────────────────────
joblib.dump(dict(
    model=r['clf'], tfidf_word=tfidf_word, tfidf_char=tfidf_char,
    use_char=r['use_char'], model_name=best,
    accuracy=r['acc'], f1_macro=r['f1'],
    labels=['NEGATIVE','NEUTRAL','POSITIVE']
), MDL_PATH)
print(f"💾 Saved → {MDL_PATH}")

# ── 6. Plots ──────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Vietnamese Sentiment Analysis — Results', fontsize=14, fontweight='bold')

# Class distribution
ax = axes[0]
vc = df['sentiment'].value_counts()
colors = ['#2ecc71','#f39c12','#e74c3c']
bars = ax.bar(vc.index, vc.values, color=colors, edgecolor='white', linewidth=1.5)
for b, v in zip(bars, vc.values):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+200,
            f'{v:,}', ha='center', fontsize=10, fontweight='bold')
ax.set_title('Class Distribution'); ax.set_ylabel('Count')
ax.set_ylim(0, vc.max()*1.15)
ax.spines[['top','right']].set_visible(False)

# Model comparison
ax = axes[1]
names = list(results.keys())
accs  = [results[n]['acc'] for n in names]
f1s   = [results[n]['f1']  for n in names]
x = np.arange(len(names)); w = 0.35
ax.bar(x-w/2, accs, w, label='Accuracy', color='#3498db', alpha=0.85)
ax.bar(x+w/2, f1s,  w, label='Macro-F1', color='#9b59b6', alpha=0.85)
ax.set_xticks(x); ax.set_xticklabels([n.replace(' ','\n') for n in names], fontsize=8)
ax.set_ylim(0.6, 1.0); ax.set_title('Model Comparison'); ax.legend()
ax.spines[['top','right']].set_visible(False)
for i,(a,f) in enumerate(zip(accs,f1s)):
    ax.text(i-w/2, a+0.004, f'{a:.3f}', ha='center', fontsize=8)
    ax.text(i+w/2, f+0.004, f'{f:.3f}', ha='center', fontsize=8)

# Confusion matrix
ax = axes[2]
cm = confusion_matrix(y_test, r['pred'], labels=['NEGATIVE','NEUTRAL','POSITIVE'])
sns.heatmap(cm.astype(float)/cm.sum(axis=1,keepdims=True)*100,
            annot=True, fmt='.1f', cmap='Blues', ax=ax,
            xticklabels=['NEG','NEU','POS'],
            yticklabels=['NEG','NEU','POS'],
            linewidths=0.5, cbar_kws={'label':'%'})
ax.set_title(f'Confusion Matrix — {best}')
ax.set_xlabel('Predicted'); ax.set_ylabel('True')

plt.tight_layout()
plt.savefig(PLOT_PATH, dpi=150, bbox_inches='tight')
print(f"📊 Plot   → {PLOT_PATH}\n✅ Done!")

"""
test_model.py — Kiểm tra model trước khi đẩy lên GitHub
=========================================================
Cách chạy:
    python tests/test_model.py

Kết quả PASS = model hoạt động tốt, sẵn sàng push lên GitHub
"""

import os, sys
import joblib
from scipy.sparse import hstack

BASE       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE, "models", "sentiment_model.joblib")

PASS = "✅ PASS"
FAIL = "❌ FAIL"
errors = []

def check(name, condition, detail=""):
    if condition:
        print(f"  {PASS}  {name}")
    else:
        print(f"  {FAIL}  {name}" + (f" — {detail}" if detail else ""))
        errors.append(name)

# ─────────────────────────────────────────────────────────────────
print("=" * 52)
print("  TEST MODEL — Vietnamese Sentiment Analysis")
print("=" * 52)

# ── Test 1: File tồn tại ─────────────────────────────────────────
print("\n[1] Kiểm tra file model")
check("File sentiment_model.joblib tồn tại",
      os.path.exists(MODEL_PATH),
      f"Không tìm thấy: {MODEL_PATH}")

if errors:
    print("\n❌ Model chưa được train. Chạy: python src/train.py")
    sys.exit(1)

# ── Test 2: Load model ───────────────────────────────────────────
print("\n[2] Load model")
try:
    obj = joblib.load(MODEL_PATH)
    check("Load file thành công", True)
except Exception as e:
    check("Load file thành công", False, str(e))
    sys.exit(1)

required_keys = ['model','tfidf_word','tfidf_char','use_char','model_name','accuracy','f1_macro']
for key in required_keys:
    check(f"Key '{key}' tồn tại", key in obj)

check("Accuracy >= 0.70", obj.get('accuracy', 0) >= 0.70,
      f"Accuracy hiện tại: {obj.get('accuracy', 0):.4f}")
check("Macro-F1 >= 0.60", obj.get('f1_macro', 0) >= 0.60,
      f"Macro-F1 hiện tại: {obj.get('f1_macro', 0):.4f}")

# ── Test 3: Inference ────────────────────────────────────────────
print("\n[3] Kiểm tra dự đoán")

MODEL      = obj['model']
TFIDF_WORD = obj['tfidf_word']
TFIDF_CHAR = obj['tfidf_char']
USE_CHAR   = obj.get('use_char', True)

def predict(texts):
    Xw = TFIDF_WORD.transform(texts)
    X  = hstack([Xw, TFIDF_CHAR.transform(texts)]) if USE_CHAR else Xw
    return MODEL.predict(X).tolist()

# Câu test rõ ràng → kỳ vọng đúng nhãn
test_cases = [
    ("chất lượng tuyệt vời giao hàng rất nhanh đóng gói đẹp", "POSITIVE"),
    ("hàng lỗi giao sai màu cửa hàng không trả lời khiếu nại", "NEGATIVE"),
    ("sản phẩm tạm được giá hơi cao so với chất lượng",        "NEUTRAL"),
    ("rất đáng tiền sẽ mua lại ủng hộ cửa hàng",              "POSITIVE"),
    ("giao thiếu hàng nhắn tin không phản hồi rất thất vọng",  "NEGATIVE"),
]

all_pass = True
for text, expected in test_cases:
    pred = predict([text])[0]
    ok   = pred == expected
    if not ok:
        all_pass = False
    emoji = {'POSITIVE':'😊','NEUTRAL':'😐','NEGATIVE':'😞'}[pred]
    status = PASS if ok else FAIL
    print(f"  {status}  [{emoji} {pred:8s}]  {text[:50]}")

if not all_pass:
    errors.append("Một số câu test dự đoán sai")

# ── Test 4: Batch inference ──────────────────────────────────────
print("\n[4] Kiểm tra batch (10 câu cùng lúc)")
import time
batch = ["hàng đẹp lắm"] * 10
t0    = time.perf_counter()
preds = predict(batch)
ms    = (time.perf_counter() - t0) * 1000
check("Batch 10 câu trả về đúng số kết quả", len(preds) == 10)
check(f"Tốc độ batch < 500ms (hiện tại: {ms:.1f}ms)", ms < 500)

# ── Test 5: Edge cases ───────────────────────────────────────────
print("\n[5] Kiểm tra edge cases")
try:
    r = predict(["a"])
    check("Câu rất ngắn (1 ký tự) không crash", True)
except:
    check("Câu rất ngắn (1 ký tự) không crash", False)

try:
    long_text = "chất lượng tốt " * 100
    r = predict([long_text])
    check("Câu rất dài (1500 ký tự) không crash", True)
except:
    check("Câu rất dài (1500 ký tự) không crash", False)

try:
    r = predict(["good quality product fast delivery"])
    check("Câu tiếng Anh không crash", True)
except:
    check("Câu tiếng Anh không crash", False)

# ── Kết quả tổng ────────────────────────────────────────────────
print("\n" + "=" * 52)
if not errors:
    print("  🎉 TẤT CẢ TESTS ĐỀU PASS")
    print("  ✅ Model sẵn sàng đẩy lên GitHub!")
else:
    print(f"  ⚠️  {len(errors)} test(s) FAIL:")
    for e in errors:
        print(f"     - {e}")
    print("  Kiểm tra lại trước khi push lên GitHub.")
print("=" * 52)

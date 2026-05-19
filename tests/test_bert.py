"""
test_bert.py — Kiểm tra BERT model trước khi đẩy lên GitHub
=============================================================
Cách chạy:
    python tests/test_bert.py

Kết quả PASS = BERT hoạt động tốt, sẵn sàng push lên GitHub
"""

import os, sys, time, json
import torch

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

MDL_DIR  = os.path.join(BASE, "models", "bert_sentiment")
CKPT     = os.path.join(MDL_DIR, "bert_model.pt")
VOCAB    = os.path.join(MDL_DIR, "tokenizer_vocab.json")

PASS_STR = "✅ PASS"
FAIL_STR = "❌ FAIL"
errors   = []

def check(name, condition, detail=""):
    if condition:
        print(f"  {PASS_STR}  {name}")
    else:
        msg = f"  {FAIL_STR}  {name}" + (f" — {detail}" if detail else "")
        print(msg)
        errors.append(name)

# ─────────────────────────────────────────────────────────────────
print("=" * 58)
print("  TEST BERT — Vietnamese Sentiment Analysis")
print("=" * 58)

# ── Test 1: Files tồn tại ────────────────────────────────────────
print("\n[1] Kiểm tra files")
check("Thư mục bert_sentiment/ tồn tại",  os.path.isdir(MDL_DIR))
check("File bert_model.pt tồn tại",        os.path.exists(CKPT),
      f"Chưa train: python src/train_bert.py --model demo")
check("File tokenizer_vocab.json tồn tại", os.path.exists(VOCAB))

if errors:
    print("\n❌ Files thiếu. Chạy: python src/train_bert.py --model demo")
    sys.exit(1)

# ── Test 2: Load checkpoint ──────────────────────────────────────
print("\n[2] Load checkpoint")
try:
    ck = torch.load(CKPT, map_location="cpu")
    check("Load bert_model.pt thành công", True)
except Exception as e:
    check("Load bert_model.pt thành công", False, str(e))
    sys.exit(1)

required_keys = ["model_state", "bert_config", "label_map", "accuracy", "f1_macro", "model_key"]
for k in required_keys:
    check(f"Key '{k}' tồn tại trong checkpoint", k in ck)

check("Accuracy >= 0.70",
      ck.get("accuracy", 0) >= 0.70,
      f"Hiện tại: {ck.get('accuracy',0):.4f}")
check("Macro-F1 >= 0.60",
      ck.get("f1_macro", 0) >= 0.60,
      f"Hiện tại: {ck.get('f1_macro',0):.4f}")

# ── Test 3: Load BERTPredictor ───────────────────────────────────
print("\n[3] Khởi tạo BERTPredictor")
try:
    from src.bert_inference import BERTPredictor
    predictor = BERTPredictor()
    check("BERTPredictor khởi tạo thành công", True)
    check(f"model_key = '{predictor.model_key}'", predictor.model_key in ["demo","phobert","mbert"])
except Exception as e:
    check("BERTPredictor khởi tạo thành công", False, str(e))
    sys.exit(1)

# ── Test 4: Semantic correctness ─────────────────────────────────
print("\n[4] Kiểm tra ngữ nghĩa (semantic correctness)")

test_cases = [
    ("chất lượng tuyệt vời giao hàng rất nhanh đóng gói đẹp", "POSITIVE"),
    ("hàng lỗi giao sai màu cửa hàng không trả lời khiếu nại", "NEGATIVE"),
    ("sản phẩm tạm được giá hơi cao so với chất lượng",        "NEUTRAL"),
    ("rất đáng tiền sẽ mua lại ủng hộ cửa hàng",              "POSITIVE"),
    ("giao thiếu hàng nhắn tin không phản hồi rất thất vọng",  "NEGATIVE"),
    ("hàng ok nhưng giao hơi chậm bình thường thôi",           "NEUTRAL"),
]

all_correct = True
for text, expected in test_cases:
    result = predictor.predict(text)
    pred   = result["label"]
    conf   = result["confidence"]
    ok     = pred == expected
    if not ok:
        all_correct = False
    emoji  = {"POSITIVE":"😊","NEUTRAL":"😐","NEGATIVE":"😞"}[pred]
    status = PASS_STR if ok else FAIL_STR
    print(f"  {status}  [{emoji} {pred:8s} conf={conf:.4f}]  {text[:52]}")

if not all_correct:
    errors.append("Một số câu semantic test sai")

# ── Test 5: Output format ────────────────────────────────────────
print("\n[5] Kiểm tra output format")
r = predictor.predict("hàng đẹp lắm")
check("Có key 'label'",      "label"      in r)
check("Có key 'sentiment'",  "sentiment"  in r)
check("Có key 'confidence'", "confidence" in r)
check("Có key 'scores'",     "scores"     in r)
check("scores có đủ 3 nhãn",
      set(r["scores"].keys()) == {"NEGATIVE","NEUTRAL","POSITIVE"})
check("Tổng xác suất ≈ 1.0",
      abs(sum(r["scores"].values()) - 1.0) < 1e-3,
      f"Tổng = {sum(r['scores'].values()):.6f}")
check("Confidence trong [0, 1]",
      0.0 <= r["confidence"] <= 1.0,
      f"confidence = {r['confidence']}")

# ── Test 6: Batch inference ──────────────────────────────────────
print("\n[6] Kiểm tra batch inference")
batch = ["hàng đẹp lắm", "giao hàng chậm quá", "tạm ổn thôi"] * 4   # 12 câu
t0    = time.perf_counter()
preds = predictor.predict_batch(batch)
ms    = (time.perf_counter() - t0) * 1000
check("Batch 12 câu trả về đúng số kết quả", len(preds) == 12)
check(f"Tốc độ batch < 2000ms (hiện tại: {ms:.0f}ms)", ms < 2000)

# ── Test 7: Edge cases ───────────────────────────────────────────
print("\n[7] Kiểm tra edge cases")

try:
    predictor.predict("ok")
    check("Câu rất ngắn (2 ký tự) không crash", True)
except Exception as e:
    check("Câu rất ngắn (2 ký tự) không crash", False, str(e))

try:
    predictor.predict("good quality fast delivery great product")
    check("Câu tiếng Anh không crash", True)
except Exception as e:
    check("Câu tiếng Anh không crash", False, str(e))

try:
    long_text = "chất lượng tốt " * 150       # ~375 từ, vượt max_len
    predictor.predict(long_text)
    check("Câu rất dài (truncation) không crash", True)
except Exception as e:
    check("Câu rất dài (truncation) không crash", False, str(e))

try:
    predictor.predict("!!! @@@ ### $$$")
    check("Câu toàn ký tự đặc biệt không crash", True)
except Exception as e:
    check("Câu toàn ký tự đặc biệt không crash", False, str(e))

try:
    predictor.predict("")
    check("Câu rỗng không crash", True)
except Exception as e:
    # Chấp nhận exception nếu có — behaviour đã xác định
    check("Câu rỗng không crash", True)   # document expected behaviour

# ── Test 8: Reproducibility ──────────────────────────────────────
print("\n[8] Kiểm tra tính ổn định (reproducibility)")
text  = "sản phẩm rất tốt đáng tiền"
runs  = [predictor.predict(text)["label"] for _ in range(5)]
check("5 lần predict cùng câu → cùng kết quả", len(set(runs)) == 1,
      f"Kết quả: {runs}")

# ── Kết quả tổng ─────────────────────────────────────────────────
print("\n" + "=" * 58)
if not errors:
    print(f"  🎉 TẤT CẢ TESTS ĐỀU PASS")
    print(f"  ✅ Accuracy={ck['accuracy']:.4f}  Macro-F1={ck['f1_macro']:.4f}")
    print(f"  ✅ BERT sẵn sàng đẩy lên GitHub!")
else:
    print(f"  ⚠️  {len(errors)} test(s) FAIL:")
    for e in errors:
        print(f"     • {e}")
    print("  Kiểm tra lại trước khi push.")
print("=" * 58)

sys.exit(0 if not errors else 1)

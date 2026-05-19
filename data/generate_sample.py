"""
generate_sample.py — Tạo dữ liệu mẫu tiếng Việt
Chạy: python data/generate_sample.py
"""
import pandas as pd, random

random.seed(42)

POSITIVE = [
    "hàng đẹp lắm chất lượng tuyệt vời", "giao hàng nhanh đóng gói cẩn thận",
    "sản phẩm đúng mô tả rất hài lòng", "chất lượng tốt giá cả hợp lý",
    "mua lần hai vẫn ổn sẽ tiếp tục ủng hộ", "shop tư vấn nhiệt tình giao đúng hẹn",
    "hàng chắc chắn bền dùng lâu dài được", "đẹp hơn ảnh thật sự ưng lắm",
    "giao siêu nhanh hài lòng hoàn toàn", "chất vải tốt may đẹp mặc thoải mái",
    "mua rất nhiều lần shop uy tín lắm", "sản phẩm chính hãng đáng tiền",
    "đóng gói kỹ hàng nguyên vẹn không bị hỏng", "màu sắc đẹp như mô tả",
    "rất đáng tiền sẽ mua lại", "shop phản hồi nhanh hỗ trợ tốt",
    "chất lượng vượt mong đợi giá lại rẻ", "giao hàng đúng giờ hàng không bị hỏng",
    "rất hài lòng sẽ giới thiệu bạn bè", "sản phẩm bền đẹp dùng thích lắm",
    "hàng thật y hình chất lượng ổn", "shop uy tín giao nhanh đóng gói đẹp",
    "mua nhiều lần đều ổn sẽ mua tiếp", "hài lòng về chất lượng và dịch vụ",
    "vừa nhận hàng đẹp quá mê luôn", "giao hàng cực nhanh đóng gói an toàn",
    "hàng đẹp chất lượng tốt giá phải chăng", "shop nhiệt tình tư vấn kỹ",
    "sản phẩm chính hãng giá tốt hài lòng", "dùng thử thấy tốt sẽ mua thêm",
    "hàng ok giao nhanh đúng hẹn", "chất lượng ổn giá hợp lý mua được",
    "shop uy tín bán hàng thật tâm", "nhận hàng nhanh chất lượng như mô tả",
    "rất ổn sẽ quay lại mua nữa", "đẹp hơn mình nghĩ thích lắm",
    "chất vải mịn mặc thoáng mát dễ chịu", "sản phẩm tốt ship nhanh hài lòng",
    "hàng đúng mô tả giá tốt ủng hộ shop", "mua về dùng thấy ok giá hợp lý",
]

NEGATIVE = [
    "hàng lỗi giao sai màu thất vọng lắm", "ship chậm quá đợi mãi không thấy",
    "chất lượng kém so với giá tiền", "mở ra hàng bị hỏng không dùng được",
    "giao thiếu hàng nhắn tin không phản hồi", "hàng không giống ảnh chất liệu rẻ tiền",
    "shop thái độ kém không hỗ trợ đổi hàng", "bị lừa hàng fake không mua nữa",
    "chất lượng quá tệ mua một lần không mua lại", "giao hàng chậm hàng lại bị hỏng",
    "sản phẩm kém chất lượng không đúng mô tả", "shop không phản hồi khi có vấn đề",
    "hàng bị lỗi liên hệ shop không giải quyết", "size không đúng không đổi trả được",
    "nhận hàng trễ hẹn nhiều ngày không xin lỗi", "hàng quá tệ đóng gói cẩu thả",
    "shop bán hàng kém chất lượng không trung thực", "mua về không dùng được yêu cầu hoàn tiền",
    "giao sai địa chỉ rồi không giải quyết", "hàng hỏng ngay sau vài ngày dùng",
    "không giống ảnh quảng cáo gian lận", "ship rất chậm hàng lại bị móp méo",
    "chất lượng cực kỳ tệ giá cao mà hàng kém", "shop thái độ hỗn láo khi khiếu nại",
    "hàng bị thiếu linh kiện shop không xử lý", "mua về thất vọng hoàn toàn",
    "hàng giả kém chất lượng không nên mua", "giao hàng trễ không thông báo",
    "hàng lỗi shop không chịu đổi rất bực", "chất liệu xấu không như mô tả",
    "mua về không dùng được tiền mất tật mang", "shop không uy tín không mua nữa đâu",
    "đóng gói cẩu thả hàng bị hỏng vỡ hết", "hàng kém chất lượng không xứng giá",
    "không phản hồi khi hàng lỗi rất bực bội", "hàng giả không chính hãng",
    "giao sai hàng rồi làm khó khi đổi trả", "chất lượng quá thấp giá lại cao",
    "hàng nhận được khác hẳn hình ảnh quảng cáo", "ship chậm hàng móp hỏng cực tệ",
]

NEUTRAL = [
    "hàng tạm ổn không có gì đặc biệt", "dùng được nhưng giá hơi cao",
    "bình thường không tệ không tốt", "hàng ok nhưng giao hơi chậm",
    "chất lượng trung bình như tầm giá", "dùng được chưa đánh giá được lâu dài",
    "hàng ổn nhưng đóng gói sơ sài", "bình thường đúng tầm giá tiền",
    "ok tạm chưa biết có mua lại không", "dùng thử thấy được nhưng chưa chắc",
    "sản phẩm bình thường không nổi bật", "tạm ổn nhưng cần cải thiện thêm",
    "hàng nhận được đúng mô tả nhưng không đặc biệt", "ok thôi không có gì ấn tượng",
    "dùng được nhưng không quá hài lòng", "bình thường không tệ lắm",
    "ship bình thường hàng ok thôi", "chưa dùng nhiều nên chưa biết",
    "trung bình không xứng với giá lắm", "hàng tạm được không thất vọng không vui",
    "ok nhưng mong đợi nhiều hơn thế", "chất lượng vừa phải không ấn tượng",
    "tạm chấp nhận được giá này", "dùng thử thấy bình thường",
    "ok không có gì đặc sắc", "nhận hàng đúng mô tả nhưng bình thường",
    "hàng ok giao bình thường không vội", "tạm ổn chưa dùng lâu chưa đánh giá được",
    "bình thường như các shop khác", "ok thôi mua vì cần thiết",
]

rows = []
for _ in range(120):
    rows.append({"clean_comment": random.choice(POSITIVE), "sentiment": "POSITIVE"})
for _ in range(120):
    rows.append({"clean_comment": random.choice(NEGATIVE), "sentiment": "NEGATIVE"})
for _ in range(80):
    rows.append({"clean_comment": random.choice(NEUTRAL),  "sentiment": "NEUTRAL"})

random.shuffle(rows)
df = pd.DataFrame(rows)
df.to_csv("data/cleaned_data.csv", index=False)
print(f"✅ Đã tạo {len(df)} mẫu → data/cleaned_data.csv")
print(df["sentiment"].value_counts().to_string())

"""
sentiment_app.py — Vietnamese Sentiment Analysis Streamlit UI
=========================================================================
A feature-rich interface for sentiment analysis using Streamlit.

Features:
- Single & Batch analysis
- CSV file upload support
- Sentiment history & trends
- Model performance metrics
- Charts and visualizations
- Dark mode toggle
- Export & copy functionality

Run with:
    streamlit run ui/sentiment_app.py
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Optional, List, Dict
import io

# ── Configuration ─────────────────────────────────────────────────
API_URL = "http://localhost:8000"
PREDICT_ENDPOINT = f"{API_URL}/predict"
BATCH_ENDPOINT = f"{API_URL}/predict/batch"
INFO_ENDPOINT = f"{API_URL}/"

# ── Page Config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="🛍️ Phân tích cảm xúc ngôn ngữ tiếng Việt",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session State Initialization ──────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "trend_data" not in st.session_state:
    st.session_state.trend_data = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "api_url" not in st.session_state:
    st.session_state.api_url = API_URL
if "single_text" not in st.session_state:
    st.session_state.single_text = ""

# ── Enhanced Styling ──────────────────────────────────────────────
def apply_theme():
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
            .main {background-color: #1e1e1e; color: #e0e0e0;}
            .sentiment-box {padding: 20px; border-radius: 10px; margin: 15px 0;}
            .positive {background-color: #1b4332; border-left: 5px solid #52b788;}
            .neutral {background-color: #5a3e3e; border-left: 5px solid #d4a574;}
            .negative {background-color: #5a2e2e; border-left: 5px solid #d46a6a;}
            .metric-card {background-color: #2a2a2a; padding: 15px; border-radius: 8px;}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            .sentiment-box {padding: 20px; border-radius: 10px; margin: 15px 0;}
            .positive {background-color: #d4edda; border-left: 5px solid #28a745;}
            .neutral {background-color: #fff3cd; border-left: 5px solid #ffc107;}
            .negative {background-color: #f8d7da; border-left: 5px solid #dc3545;}
            .metric-card {background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6;}
        </style>
        """, unsafe_allow_html=True)

apply_theme()

# ── Example Templates ─────────────────────────────────────────────
EXAMPLES = {
    "😊 Positive": "chất lượng tuyệt vời giao hàng rất nhanh shop tuyệt vời",
    "😐 Neutral": "sản phẩm bình thường giá hợp lý",
    "😞 Negative": "hàng kém chất lượng giao sai địa chỉ không đáng tiền"
}

# ── Helper Functions ──────────────────────────────────────────────
def get_model_info():
    """Fetch model performance metrics from API."""
    try:
        response = requests.get(st.session_state.api_url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def predict_single(text: str) -> Optional[Dict]:
    """Send single text to API for sentiment analysis."""
    try:
        response = requests.post(
            f"{st.session_state.api_url}/predict",
            json={"text": text},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def predict_batch(texts: List[str]) -> Optional[Dict]:
    """Send batch texts to API for sentiment analysis."""
    try:
        response = requests.post(
            f"{st.session_state.api_url}/predict/batch",
            json={"texts": texts},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def add_to_history(text: str, result: Dict):
    """Add analysis to history and trend data."""
    entry = {
        "timestamp": datetime.now(),
        "text": text,
        "sentiment": result.get("sentiment", "Unknown"),
        "label": result.get("label", "Unknown"),
        "confidence": result.get("confidence", 0)
    }
    st.session_state.history.append(entry)
    st.session_state.trend_data.append({
        "timestamp": entry["timestamp"],
        "label": entry["label"],
        "confidence": entry["confidence"]
    })

def export_to_csv(data: List[Dict]) -> bytes:
    """Convert analysis data to CSV."""
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode()

def set_example_text(example_text: str):
    """Callback to set example text in session state."""
    st.session_state.single_text = example_text

# ── Header ────────────────────────────────────────────────────────
st.title("🛍️ Phân tích cảm xúc ngôn ngữ tiếng Việt")
st.markdown("Phân tích nhận xét sản phẩm tiếng Việt")
st.markdown("Nhập văn bản tiếng Việt để phân tích cảm xúc: POSITIVE, NEUTRAL, NEGATIVE")

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Cài đặt")
    
    # Dark Mode Toggle
    st.session_state.dark_mode = st.checkbox("🌙 Dark Mode", value=st.session_state.dark_mode)
    
    # API Configuration
    st.session_state.api_url = st.text_input("API URL:", value=st.session_state.api_url)
    
    # Test Connection
    if st.button("🧪 Kiểm tra kết nối", width="stretch"):
        try:
            response = requests.get(f"{st.session_state.api_url}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ API trực tuyến và hoạt động tốt!")
                model_info = get_model_info()
                if model_info:
                    st.metric("Accuracy", f"{model_info.get('accuracy', 0):.2%}")
                    st.metric("F1 Score", f"{model_info.get('f1_macro', 0):.2%}")
            else:
                st.error("❌ API trả về lỗi. Vui lòng kiểm tra lại.")
        except Exception as e:
            st.error(f"❌ Cannot reach API: {e}")
    
    st.divider()
    
    # Model Info
    st.markdown("### 📊 Thông tin Mô hình")
    model_info = get_model_info()
    if model_info:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Accuracy", f"{model_info.get('accuracy', 0):.2%}")
        with col2:
            st.metric("F1 Score", f"{model_info.get('f1_macro', 0):.2%}")
        st.caption(f"Mô hình: {model_info.get('model', 'Unknown')}")
    
    st.divider()
    
    # About
    st.markdown("### ℹ️ Thông tin")
    st.markdown("""
    **Classification:**
    - 😊 **POSITIVE**: Cảm xúc tích cực
    - 😐 **NEUTRAL**: Cảm xúc trung lập
    - 😞 **NEGATIVE**: Cảm xúc tiêu cực

    **Hướng dẫn:**
    - Tối đa 2000 ký tự cho phân tích đơn lẻ
    - Tối đa 100 văn bản cho phân tích hàng loạt
    - Sử dụng tiếng Việt có dấu để có kết quả chính xác nhất
    """)
    
    st.divider()
    
    # History Stats
    if st.session_state.history:
        st.markdown("### 📈 Thống kê phiên làm việc")
        history_df = pd.DataFrame(st.session_state.history)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tổng số đã phân tích", len(st.session_state.history))
        with col2:
            positive = (history_df["label"] == "POSITIVE").sum()
            st.metric("Tích cực", positive)
        with col3:
            negative = (history_df["label"] == "NEGATIVE").sum()
            st.metric("Tiêu cực", negative)

# ── Main Tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Phân tích đơn lẻ",
    "📦 Phân tích hàng loạt",
    "📊 Thống kê",
    "📜 Lịch sử"
])

# ══════════════════════════════════════════════════════════════════
# TAB 1: Single Analysis
# ══════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 🔍 Phân tích văn bản đơn lẻ")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Character counter
        user_text = st.text_area(
            "Nhập văn bản tiếng Việt:",
            placeholder="e.g., chất lượng tuyệt vời giao hàng rất nhanh",
            height=120,
            help="Tối đa 2000 ký tự",
            key="single_text"
        )
        char_count = len(user_text)
        st.progress(min(char_count / 2000, 1.0))
        st.caption(f"Ký tự: {char_count}/2000")
    
    with col2:
        st.markdown("### Ví dụ")
        for label, example in EXAMPLES.items():
            st.button(
                label,
                width="stretch",
                key=f"example_{label}",
                on_click=set_example_text,
                args=(example,)
            )
    
    st.markdown("---")
    
    # Input Suggestions
    if user_text:
        suggestions = []
        if "  " in user_text:
            suggestions.append("💡 Xóa khoảng trắng thừa")
        if any(char.isupper() for char in user_text):
            suggestions.append("💡 Chuyển văn bản sang chữ thường để cải thiện kết quả")
        if len(user_text.split()) < 2:
            suggestions.append("💡 Văn bản dài hơn sẽ cung cấp ngữ cảnh tốt hơn")
        
        if suggestions:
            with st.expander("💡 Gợi ý đầu vào"):
                for suggestion in suggestions:
                    st.info(suggestion)
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_button = st.button("🔍 Phân tích Cảm xúc", width="stretch", key="single_analyze")
    
    st.markdown("---")
    
    # Result Display
    if analyze_button:
        if not user_text.strip():
            st.error("❌ Vui lòng nhập văn bản để phân tích.")
        else:
            with st.spinner("Đang phân tích cảm xúc..."):
                result = predict_single(user_text)
                
                if result:
                    sentiment = result.get("sentiment", "Unknown")
                    label = result.get("label", "Unknown")
                    confidence = result.get("confidence", 0)
                    
                    # Add to history
                    add_to_history(user_text, result)
                    
                    # Determine styling class
                    style_class = label.lower() if label.lower() in ["positive", "neutral", "negative"] else "neutral"
                    
                    # Display result
                    st.markdown(f"""
                    <div class="sentiment-box {style_class}">
                        <h3>📊 Kết quả Phân tích</h3>
                        <p><b>Cảm xúc:</b> {sentiment}</p>
                        <p><b>Độ tin cậy:</b> {confidence:.2%}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Copy & Export
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        copy_text = json.dumps(result, indent=2, ensure_ascii=False)
                        st.download_button(
                            "📋 Sao chép kết quả (JSON)",
                            copy_text,
                            file_name=f"sentiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            width="stretch"
                        )
                    with col2:
                        csv_data = export_to_csv([{
                            "Text": user_text,
                            "Sentiment": sentiment,
                            "Label": label,
                            "Confidence": f"{confidence:.2%}"
                        }])
                        st.download_button(
                            "📊 Xuất file CSV",
                            csv_data,
                            file_name=f"sentiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            width="stretch"
                        )
                    
                    with st.expander("📋 Raw response"):
                        st.json(result)
                
                else:
                    st.error("❌ Phân tích thất bại. Vui lòng thử lại sau.")

# ══════════════════════════════════════════════════════════════════
# TAB 2: Batch Analysis
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Phân tích hàng loạt")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Lựa chọn 1: Tải lên file CSV")
        st.markdown("File CSV phải có một cột chứa văn bản cần phân tích. Tối đa 100 văn bản.")
        uploaded_file = st.file_uploader("Chọn file CSV", type="csv", key="batch_csv")
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("Xem trước:", df.head())
            
            text_column = st.selectbox("Chọn cột văn bản:", df.columns)
            
            if st.button("🚀 Phân tích hàng loạt (CSV)", width="stretch"):
                texts = df[text_column].astype(str).tolist()[:100]  # Max 100
                
                with st.spinner(f"Đang phân tích {len(texts)} văn bản..."):
                    batch_result = predict_batch(texts)
                    
                    if batch_result:
                        results = batch_result.get("results", [])
                        latency = batch_result.get("latency_ms", 0)
                        
                        # Create results dataframe
                        results_df = pd.DataFrame([{
                            "Text": r["text"],
                            "Sentiment": r["sentiment"],
                            "Label": r["label"],
                            "Confidence": r["confidence"]
                        } for r in results])
                        
                        # Add all to history
                        for r in results:
                            add_to_history(r["text"], r)
                        
                        st.success(f"✅ Đã phân tích {len(results)} văn bản trong {latency}ms")
                        st.dataframe(results_df, width="stretch")
                        
                        # Export
                        csv_data = results_df.to_csv(index=False).encode()
                        st.download_button(
                            "📊 Tải về Kết quả",
                            csv_data,
                            file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            width="stretch"
                        )
                    else:
                        st.error("❌ Phân tích hàng loạt thất bại.")
    
    with col2:
        st.markdown("#### Lựa chọn 2: Dán nhiều văn bản")
        batch_text = st.text_area(
            "Dán nhiều văn bản (mỗi dòng một văn bản, tối đa 100 dòng):",
            height=200,
            placeholder="Line 1: Review thứ nhất\nLine 2: Review thứ hai\nLine 3: Review thứ ba"
        )
        
        if st.button("🚀 Phân tích hàng loạt (Dán)", width="stretch"):
            texts = [t.strip() for t in batch_text.split("\n") if t.strip()][:100]
            
            if not texts:
                st.error("❌ Vui lòng nhập ít nhất một văn bản để phân tích.")
            else:
                with st.spinner(f"Đang phân tích {len(texts)} văn bản..."):
                    batch_result = predict_batch(texts)
                    
                    if batch_result:
                        results = batch_result.get("results", [])
                        latency = batch_result.get("latency_ms", 0)
                        
                        # Create results dataframe
                        results_df = pd.DataFrame([{
                            "Text": r["text"],
                            "Sentiment": r["sentiment"],
                            "Label": r["label"],
                            "Confidence": r["confidence"]
                        } for r in results])
                        
                        # Add all to history
                        for r in results:
                            add_to_history(r["text"], r)
                        
                        st.success(f"✅ Đã phân tích {len(results)} văn bản trong {latency}ms")
                        st.dataframe(results_df, width="stretch")
                        
                        # Export
                        csv_data = results_df.to_csv(index=False).encode()
                        st.download_button(
                            "📊 Tải về Kết quả",
                            csv_data,
                            file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            width="stretch"
                        )
                    else:
                        st.error("❌ Phân tích hàng loạt thất bại.")

# ══════════════════════════════════════════════════════════════════
# TAB 3: Analytics
# ══════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Thống kê kết quả Phân tích cảm xúc")
    
    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history)
        
        # Sentiment Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Phân bố Cảm xúc")
            sentiment_counts = history_df["label"].value_counts()
            
            fig = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                color_discrete_map={
                    "POSITIVE": "#28a745",
                    "NEUTRAL": "#ffc107",
                    "NEGATIVE": "#dc3545"
                }
            )
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            st.markdown("#### Phân bố Độ tin cậy")
            fig = px.histogram(
                history_df,
                x="confidence",
                nbins=20,
                title="Confidence Scores Distribution",
                labels={"confidence": "Confidence"}
            )
            st.plotly_chart(fig, width="stretch")
        
        # Sentiment Trend
        if len(st.session_state.trend_data) > 1:
            st.markdown("#### xu hướng Cảm xúc theo thời gian")
            trend_df = pd.DataFrame(st.session_state.trend_data)
            
            fig = go.Figure()
            for label in ["POSITIVE", "NEUTRAL", "NEGATIVE"]:
                label_data = trend_df[trend_df["label"] == label]
                fig.add_trace(go.Scatter(
                    x=label_data["timestamp"],
                    y=label_data["confidence"],
                    mode="lines+markers",
                    name=label,
                    marker=dict(size=8),
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                title="Confidence Trend",
                xaxis_title="Time",
                yaxis_title="Confidence",
                hovermode="x unified"
            )
            st.plotly_chart(fig, width="stretch")
        
        # Statistics
        st.markdown("#### Thống kê chung")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Tổng số phân tích", len(history_df))
        with col2:
            avg_confidence = history_df["confidence"].mean()
            st.metric("Độ tin cậy trung bình", f"{avg_confidence:.2%}")
        with col3:
            positive_pct = (history_df["label"] == "POSITIVE").sum() / len(history_df) * 100
            st.metric("Tỷ lệ Positive", f"{positive_pct:.1f}%")
        with col4:
            negative_pct = (history_df["label"] == "NEGATIVE").sum() / len(history_df) * 100
            st.metric("Tỷ lệ Negative", f"{negative_pct:.1f}%")
    
    else:
        st.info("📊 Chưa có dữ liệu phân tích. Phân tích một số văn bản để xem thống kê.")

# ══════════════════════════════════════════════════════════════════
# TAB 4: History
# ══════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### Lịch sử phân tích")
    
    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sentiment_filter = st.multiselect(
                "Lọc theo Cảm xúc:",
                ["POSITIVE", "NEUTRAL", "NEGATIVE"],
                default=["POSITIVE", "NEUTRAL", "NEGATIVE"]
            )
        
        with col2:
            min_confidence = st.slider("Min Confidence:", 0.0, 1.0, 0.0)
        
        with col3:
            if st.button("🗑️ Xóa lịch sử", width="stretch"):
                st.session_state.history = []
                st.session_state.trend_data = []
                st.rerun()
        
        # Filter data
        filtered_df = history_df[
            (history_df["label"].isin(sentiment_filter)) &
            (history_df["confidence"] >= min_confidence)
        ].copy()
        
        # Display
        st.dataframe(
            filtered_df[[
                "timestamp",
                "text",
                "sentiment",
                "label",
                "confidence"
            ]].rename(columns={
                "timestamp": "Time",
                "text": "Text",
                "sentiment": "Sentiment",
                "label": "Label",
                "confidence": "Confidence"
            }),
            width="stretch",
            hide_index=True
        )
        
        # Export all history
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = filtered_df.to_csv(index=False).encode()
            st.download_button(
                "📊 Xuất lịch sử đã lọc",
                csv_data,
                file_name=f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                width="stretch"
            )
        
        with col2:
            # Convert timestamp to string for JSON serialization
            export_df = filtered_df.copy()
            export_df["timestamp"] = export_df["timestamp"].astype(str)
            json_data = json.dumps(export_df.to_dict(orient="records"), indent=2, ensure_ascii=False).encode()
            st.download_button(
                "📋 Xuất dưới dạng JSON",
                json_data,
                file_name=f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                width="stretch"
            )
    
    else:
        st.info("📜 Chưa có lịch sử phân tích. Phân tích một số văn bản để xem tại đây.")

# 🛍️ Vietnamese Sentiment Analysis — Streamlit UI Guide

A feature-rich web interface for analyzing Vietnamese product reviews and comments using sentiment analysis.

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [User Guide](#user-guide)
- [API Configuration](#api-configuration)
- [Features Overview](#features-overview)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

- **Single Text Analysis**: Analyze individual Vietnamese texts for sentiment
- **Batch Analysis**: Process multiple texts at once via CSV upload or paste
- **Sentiment History**: Track all analyses with timestamps and confidence scores
- **Analytics Dashboard**: Visualize sentiment distribution and trends
- **Dark Mode**: Toggle between light and dark themes
- **Export Results**: Download analysis results in CSV or JSON format
- **Real-time Metrics**: View model accuracy and F1 scores
- **Input Suggestions**: Get recommendations for better analysis results

---

## 📦 Prerequisites

- **Python 3.8+**
- **Streamlit** (`pip install streamlit`)
- **FastAPI Backend**: The app connects to a sentiment analysis API running on `http://localhost:8000`
- **Additional Libraries**: pandas, plotly, requests

---

## 🔧 Installation

### 1. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install streamlit pandas plotly requests
```

### 3. Ensure API is Running

Before starting the Streamlit app, make sure the FastAPI backend is running:

```bash
# From the project root
python -m uvicorn api.main:app --reload --host localhost --port 8000
```

---

## 🚀 Running the Application

From the project root directory, run:

```bash
streamlit run ui/sentiment_app.py
```

The app will open in your default browser at `http://localhost:8501`

---

## 📖 User Guide

### 🔍 Tab 1: Single Analysis (Phân tích đơn lẻ)

**Analyze a single Vietnamese text:**

1. **Input Text**: 
   - Type or paste Vietnamese text in the text area
   - Maximum 2000 characters
   - Use Vietnamese with diacritics for best results (e.g., "chất lượng tuyệt vời")

2. **Example Templates**: 
   - Click any example button to quickly load pre-written sentiments
   - Options:
     - 😊 **Positive**: "chất lượng tuyệt vời giao hàng rất nhanh shop tuyệt vời"
     - 😐 **Neutral**: "sản phẩm bình thường giá hợp lý"
     - 😞 **Negative**: "hàng kém chất lượng giao sai địa chỉ không đáng tiền"

3. **Input Suggestions**:
   - Expand "💡 Gợi ý đầu vào" for recommendations
   - Remove extra spaces, use lowercase, provide context

4. **Analyze**:
   - Click "🔍 Phân tích Cảm xúc" button
   - View results showing:
     - Sentiment label (POSITIVE, NEUTRAL, NEGATIVE)
     - Confidence score (0-100%)

5. **Export**:
   - Download results as **JSON** or **CSV**
   - View raw API response

---

### 📦 Tab 2: Batch Analysis (Phân tích hàng loạt)

**Analyze multiple texts at once:**

#### Option 1: Upload CSV File

1. Click "Chọn file CSV" to upload
2. File must contain text data (columns can be any name)
3. Select the text column from dropdown
4. Click "🚀 Phân tích hàng loạt (CSV)"
5. Results display in table format with download button
6. **Maximum 100 texts per batch**

#### Option 2: Paste Multiple Texts

1. Paste texts in the text area (one line per text)
2. Click "🚀 Phân tích hàng loạt (Dán)"
3. View results table and processing latency
4. Download results as CSV
5. **Maximum 100 texts per batch**

**CSV File Format Example:**
```
text,other_column
chất lượng tuyệt vời,product_1
hàng kém chất lượng,product_2
sản phẩm bình thường,product_3
```

---

### 📊 Tab 3: Analytics (Thống kê)

**Visualize sentiment analysis results:**

- **Pie Chart**: Sentiment distribution (Positive/Neutral/Negative percentages)
- **Histogram**: Confidence score distribution
- **Trend Chart**: Confidence scores over time (appears after multiple analyses)
- **Statistics Summary**:
  - Total analyses
  - Average confidence
  - Positive percentage
  - Negative percentage

**Available after analyzing texts. Refreshes automatically.**

---

### 📜 Tab 4: History (Lịch sử)

**Review and export all analyses:**

1. **Filter Options**:
   - Filter by sentiment label (Positive/Neutral/Negative)
   - Set minimum confidence threshold
   - Multiple selections allowed

2. **History Table**:
   - Timestamp
   - Original text
   - Sentiment label
   - Confidence score

3. **Clear History**: 
   - Click "🗑️ Xóa lịch sử" to reset
   - Cannot be undone

4. **Export**:
   - Download filtered results as **CSV**
   - Download filtered results as **JSON**

---

## ⚙️ API Configuration (Sidebar)

### Connection Settings

- **API URL**: Default `http://localhost:8000`
  - Modify if your API runs on a different address/port
  - Changes apply immediately

### Test Connection

- Click "🧪 Kiểm tra kết nối" to verify API is reachable
- Displays model accuracy and F1 score if successful
- Shows error message if connection fails

### Dark Mode

- Toggle "🌙 Dark Mode" for theme preference
- Persists during your session

### Model Information

- **Accuracy**: Model's overall correctness percentage
- **F1 Score**: Macro-averaged F1 score across all classes
- **Model Name**: Type of model being used

---

## 🛠️ Features Explained

### Sentiment Classifications

- **😊 POSITIVE**: Positive/favorable sentiment (happy, satisfied, recommended)
- **😐 NEUTRAL**: Neutral/factual sentiment (neither positive nor negative)
- **😞 NEGATIVE**: Negative/unfavorable sentiment (dissatisfied, problems, complaints)

### Confidence Score

- Ranges from 0% to 100%
- Higher percentage = higher model confidence in the prediction
- 80%+ = typically reliable
- Below 60% = consider the result carefully

### Input Tips

- Use Vietnamese with proper diacritics (phẩy, mũi, huyền, sắc, hỏi, ngã)
- Provide context (2+ words minimum)
- Avoid excessive spaces or special characters
- Mixed languages may reduce accuracy

---

## 🐛 Troubleshooting

### "❌ Cannot reach API"

**Problem**: Connection refused or timeout
- **Solution 1**: Check if FastAPI backend is running on port 8000
  ```bash
  python -m uvicorn api.main:app --reload --host localhost --port 8000
  ```
- **Solution 2**: Verify API URL in sidebar settings
- **Solution 3**: Check firewall/network settings

### "❌ Phân tích thất bại"

**Problem**: Analysis fails but API is running
- **Solution 1**: Check API logs for errors
- **Solution 2**: Verify input text format and encoding
- **Solution 3**: Try shorter input text

### Performance is Slow

**Problem**: Batch analysis takes too long
- **Solution 1**: Reduce batch size (split into smaller groups)
- **Solution 2**: Check system resources (RAM, CPU)
- **Solution 3**: Check API server performance

### Text Area Not Updating

**Problem**: Example buttons don't fill text area
- **Solution**: Clear browser cache or try refreshing the page
- The text area uses session state, clearing it resets values

### Export Not Working

**Problem**: Download buttons don't respond
- **Solution 1**: Try a different browser
- **Solution 2**: Check browser download settings
- **Solution 3**: Use clipboard copy instead (📋 buttons)

---

## 📁 Project Structure

```
SentimentAnalysis/
├── api/
│   └── main.py              # FastAPI backend
├── ui/
│   └── sentiment_app.py     # Streamlit frontend (THIS FILE)
├── src/
│   └── train.py             # Model training
├── models/
│   └── sentiment_model.joblib # Trained model
├── data/
│   ├── raw_data.csv
│   └── clean_data.csv
├── requirements.txt
└── README.md
```

---

## 💡 Tips & Best Practices

1. **Batch Processing**: Use Tab 2 for analyzing large datasets (more efficient)
2. **Export Results**: Regularly export history to avoid losing data on session refresh
3. **Model Accuracy**: Check model info in sidebar for expected performance
4. **Filtering**: Use Tab 4 filters to find specific analyses in your history
5. **Dark Mode**: Easier on eyes during extended use

---

## 📝 Example Workflows

### Workflow 1: Quick Single Analysis

1. Go to Tab 1
2. Click an example button or paste text
3. Click "🔍 Phân tích Cảm xúc"
4. View results

### Workflow 2: Batch CSV Analysis

1. Prepare CSV file with text column
2. Go to Tab 2
3. Upload CSV
4. Select text column
5. Click analyze
6. Download results

### Workflow 3: Track Sentiment Trends

1. Analyze multiple texts (Tab 1 or 2)
2. Go to Tab 3 to view visualizations
3. Check analytics and trends
4. Use Tab 4 to filter and export

---

## 🔒 Session & Data

- **Session State**: Persists during your browser session
- **History**: Stored in session memory (cleared on refresh)
- **Exports**: Downloaded files are permanent
- **Settings**: Dark mode and API URL saved in current session

---

## 📞 Support

For issues or questions:
- Check logs in API terminal
- Verify environment setup
- Review error messages in Streamlit UI
- Check sidebar model info for API status

---

**Last Updated**: May 2026
**Version**: 1.0

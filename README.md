# Sentiment Analysis
This is a warm-up project for course AIO 2026
# 📊 AI Sentiment Analysis System

![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Python](https://img.shields.io/badge/Python-green)

A full **end-to-end system** for sentiment analysis including:
- Model training pipeline
- FastAPI inference service
- Streamlit UI dashboard
- Automated testing (API / Model / UI)
- Dockerized environment
- CI/CD with GitHub Actions
- Auto-generated reports (PDF + PNG)

---
# 📁 1. Project Structure
```text
AI Sentiment System
│
├── models/              # training pipeline
├── api/                 # FastAPI backend
├── ui/                  # Streamlit UI
├── tests/               # API / Model / UI tests
├── reports/             # generated test reports
├── ci.sh                # local CI pipeline
├── docker-compose.yml   # full system orchestration
└── .github/workflows/   # GitHub CI pipeline
```
---
# 🐳 2. Run Project with Docker

## 🔧 Build system

```bash
docker compose build
```
## 🚀 Start services
```bash
docker compose up -d model api ui
```
Services:
API → http://localhost:8000/docs⁠
UI → http://localhost:8501⁠
## 🧪 Run tests manually
```bash
docker compose run --rm test-model
docker compose run --rm test-api
docker compose run --rm test-ui
```
---
# ⚙️ 3. Run Full CI Pipeline (Local)
## 🚀 Execute CI script
```bash
bash ci.sh
```
## 📌 CI workflow includes:
```text
✔ Build Docker images
✔ Start API + UI
✔ Wait for services
✔ Run Model tests
✔ Run API tests
✔ Run UI tests
✔ Generate reports (PDF + charts)
✔ Cleanup containers
```
---
# 📊 4. Test Reports
After CI execution, reports are generated:
```text
reports/
├── api_test_results.pdf
├── model_test_results.png
```
---
# ⚙️ 5. GitHub Actions CI/CD
## 🚀 Trigger events
```text
✔ Push to main
✔ Pull request
```
## 📌 CI pipeline steps
```text
✔ Checkout code
✔ Build Docker images
✔ Start MODEL + API + UI
✔ Run tests
✔ Generate reports
✔ Upload artifacts
✔ Cleanup
```
## 📦 Download CI reports
```text
After workflow runs:
✔ Go to GitHub → Actions
✔ Select latest run
✔ Download artifact: test-reports/
```
---
# 🧠 Summary
```text
This project provides:
✔ Full Docker ML system
✔ Automated CI/CD pipeline
✔ Model + API + UI testing
✔ Report generation (PDF + charts)
✔ GitHub Actions integration
✔ Production-ready structure
```
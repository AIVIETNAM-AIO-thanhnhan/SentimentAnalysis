"""
test_api.py — Kiểm tra API trước khi đẩy lên GitHub
=========================================================
Cách chạy:
    pytest tests/test_api.py -v -s

Kết quả:
    - Chạy toàn bộ API test từ CSV
    - Verify Expected_Result
    - Export PDF file report tự động
"""

import os
import csv
import ast
import requests
import pytest
import matplotlib.pyplot as plt
from matplotlib import font_manager

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime


BASE_URL = "http://localhost:8000"

BASE = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

TEST_DIR = os.path.join(
    BASE,
    "tests"
)

CSV_FILE = os.path.join(
    TEST_DIR,
    "api_testcase.csv"
)

font_path = os.path.join(
    TEST_DIR,
    "NotoSans-Regular.ttf"
)

font_manager.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'Noto Sans'


TEST_RESULT_PATH = os.path.join(
    TEST_DIR,
    "api_test_results.pdf"
)

os.makedirs(
    TEST_DIR,
    exist_ok=True
)

TIMEOUT = 15

TEST_RESULTS = []


# =========================================================
# Load Testcases
# =========================================================

def load_test_cases():

    test_cases = []

    with open(
        CSV_FILE,
        newline="",
        encoding="utf-8-sig"
    ) as csvfile:

        reader = csv.DictReader(
            csvfile
        )

        for row in reader:

            test_cases.append(
                row
            )

    return test_cases


TEST_CASES = load_test_cases()


# =========================================================
# Save Test Result
# =========================================================

def save_test_result(
    tc_id,
    category,
    status,
    error_message=""
):

    TEST_RESULTS.append({
        "tc_id": tc_id,
        "category": category,
        "status": status,
        "error": error_message
    })


# =========================================================
# Main API Test
# =========================================================

@pytest.mark.parametrize(
    "tc",
    TEST_CASES,
    ids = [
        tc["TC_ID"]
        for tc in TEST_CASES
    ]
)
def test_api(tc):

    endpoint = tc["Endpoint"]

    method = tc["Method"].upper()

    expected_status = int(
        tc["Expected_Status"]
    )

    request_body = tc["Request_Body"]

    tc_id = tc["TC_ID"]

    category = tc["Category"]

    url = f"{BASE_URL}{endpoint}"

    headers = {
        "Content-Type": "application/json"
    }

    json_body = None

    if request_body:

        try:

            json_body = ast.literal_eval(
                request_body
            )

        except Exception:

            json_body = None

    status = "PASSED"

    error_message = ""

    try:

        # -----------------------------------
        # GET
        # -----------------------------------

        if method == "GET":

            response = requests.get(
                url,
                headers=headers,
                timeout=TIMEOUT
            )

        # -----------------------------------
        # POST
        # -----------------------------------

        elif method == "POST":

            response = requests.post(
                url,
                json=json_body,
                headers=headers,
                timeout=TIMEOUT
            )

        else:

            status = "FAILED"

            error_message = (
                f"Unsupported method: {method}"
            )

            pytest.fail(
                f"[{tc_id}] Unsupported method: {method}"
            )

        # -----------------------------------
        # Status Validation
        # -----------------------------------

        assert response.status_code == expected_status, (
            f"\n"
            f"========== STATUS CODE FAILED ==========\n"
            f"TC_ID       : {tc_id}\n"
            f"Category    : {category}\n"
            f"Endpoint    : {endpoint}\n"
            f"Input       : {request_body}\n"
            f"Expected    : {expected_status}\n"
            f"Actual      : {response.status_code}\n"
            f"Response    : {response.text}\n"
            f"========================================\n"
        )

        # -----------------------------------
        # Business Validation
        # -----------------------------------

        validate_response(
            tc,
            response
        )

    except AssertionError as e:

        status = "FAILED"

        error_message = str(e)

        pytest.fail(str(e))

    except requests.exceptions.Timeout:

        status = "FAILED"

        error_message = "Request timeout"

        pytest.fail(
            f"[{tc_id}] Request timeout"
        )

    except requests.exceptions.ConnectionError:

        status = "FAILED"

        error_message = (
            "Cannot connect to API server"
        )

        pytest.fail(
            f"[{tc_id}] Cannot connect to API server"
        )

    except Exception as e:

        status = "FAILED"

        error_message = str(e)

        pytest.fail(
            f"[{tc_id}] Unexpected error: {str(e)}"
        )

    finally:

        save_test_result(
            tc_id=tc_id,
            category=category,
            status=status,
            error_message=error_message
        )


# =========================================================
# Response Validation
# =========================================================

def validate_response(
    tc,
    response
):

    tc_id = tc["TC_ID"]
    body_request = tc["Request_Body"]
    category = tc["Category"]

    endpoint = tc["Endpoint"]

    expected_result = (
        str(
            tc.get(
                "Expected_Result",
                ""
            )
        )
        .strip()
        .lower()
    )

    content_type = response.headers.get(
        "Content-Type",
        ""
    )

    if response.status_code == 200:

        assert (
            "application/json"
            in content_type.lower()
        ), (
            f"[{tc_id}] Invalid content type: {content_type}"
        )

        try:

            data = response.json()

        except Exception:

            pytest.fail(
                f"[{tc_id}] Invalid JSON response"
            )

        # ===================================
        # /health
        # ===================================

        if endpoint == "/health":

            assert isinstance(
                data,
                dict
            ), (
                f"[{tc_id}] "
                f"/health response must be object"
            )

            response_text = str(data).lower()

            if expected_result:

                assert (
                    expected_result
                    in response_text
                ), (
                    f"[{tc_id}] "
                    f"Expected '{expected_result}' "
                    f"but got {data}"
                )

        # ===================================
        # /predict
        # ===================================

        elif endpoint == "/predict":

            assert isinstance(
                data,
                dict
            ), (
                f"[{tc_id}] "
                f"Response should be object"
            )

            possible_fields = [
                "label",
                "prediction",
                "sentiment"
            ]

            prediction_field = None

            for field in possible_fields:

                if field in data:

                    prediction_field = field

                    break

            assert prediction_field, (
                f"[{tc_id}] "
                f"Missing prediction field"
            )

            actual_prediction = str(
                data[prediction_field]
            ).lower()

            if expected_result:

                assert (
                        actual_prediction
                        == expected_result
                    ), (
                        f"[{tc_id}] "
                        f"[endpoint: {endpoint}]"
                        f"[request: {body_request}] "
                        f"Expected sentiment "
                        f"'{expected_result}' "
                        f"but got "
                        f"'{actual_prediction}'"
                    )

        # ===================================
        # /predict/batch
        # ===================================

        elif endpoint == "/predict/batch":

            assert isinstance(
                data,
                (dict, list)
            ), (
                f"[{tc_id}] "
                f"Invalid batch response type"
            )


# =========================================================
# Load Test
# =========================================================

def run_load_test(
    endpoint="/predict",
    total_requests=100,
    concurrent_users=10
):

    url = f"{BASE_URL}{endpoint}"

    payload = {
        "text": "Sản phẩm rất tốt"
    }

    def send_request():

        try:

            response = requests.post(
                url,
                json=payload,
                timeout=TIMEOUT
            )

            return response.status_code

        except Exception:

            return None

    with ThreadPoolExecutor(
        max_workers=concurrent_users
    ) as executor:

        results = list(
            executor.map(
                lambda _: send_request(),
                range(total_requests)
            )
        )

    success_count = sum(
        1 for r in results
        if r == 200
    )

    failed_count = (
        total_requests - success_count
    )

    print("\n=== LOAD TEST RESULT ===")

    print(f"Total Requests : {total_requests}")

    print(f"Concurrent Users: {concurrent_users}")

    print(f"Success         : {success_count}")

    print(f"Failed          : {failed_count}")

import os
import requests
import matplotlib.pyplot as plt

from collections import Counter
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
    Preformatted
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.lib.pagesizes import A4


def generate_test_report(results):

    total = len(results)

    passed = sum(
        1 for r in results
        if r["status"] == "PASSED"
    )

    failed = sum(
        1 for r in results
        if r["status"] == "FAILED"
    )

    skipped = sum(
        1 for r in results
        if r["status"] == "SKIPPED"
    )

    categories = [
        r["category"]
        for r in results
    ]

    category_counter = Counter(categories)

    failed_results = [
        r for r in results
        if r["status"] == "FAILED"
    ]

    failed_category_counter = Counter(
        r["category"]
        for r in failed_results
    )
    pdfmetrics.registerFont(
        TTFont(
            "NotoSans",
            font_path
        )
    )

    # =====================================================
    # Create Charts
    # =====================================================

    plt.rcParams["font.family"] = "DejaVu Sans"

    fig = plt.figure(figsize=(18, 12))

    fig.suptitle(
        "Vietnamese Sentiment API - Enterprise QA Report",
        fontsize=22,
        fontweight="bold"
    )

    # Chart 1
    ax1 = plt.subplot2grid((3, 3), (0, 0))

    ax1.bar(
        ["Passed", "Failed", "Skipped"],
        [passed, failed, skipped]
    )

    ax1.set_title("Test Result Distribution")
     
    # Chart 2
    ax2 = plt.subplot2grid((3, 3), (0, 1))

    ax2.pie(
        [passed, failed, skipped],
        labels=["Passed", "Failed", "Skipped"],
        autopct="%1.1f%%"
    )

    ax2.set_title("Pass Rate")

    # Chart 3
    ax3 = plt.subplot2grid((3, 3), (0, 2))

    ax3.barh(
        list(category_counter.keys()),
        list(category_counter.values())
    )

    ax3.set_title(
        "Test Cases by Category"
    )

    # Chart 4
    ax4 = plt.subplot2grid(
        (3, 3),
        (1, 0),
        colspan=3
    )

    if failed_category_counter:

        ax4.barh(
            list(failed_category_counter.keys()),
            list(failed_category_counter.values())
        )

        ax4.set_title(
            "Failed Test Cases by Category"
        )

    else:

        ax4.text(
            0.5,
            0.5,
            "No Failed Test Cases",
            ha="center",
            va="center"
        )

    chart_path = "temp_report_chart.png"

    plt.tight_layout(
        rect=[0, 0, 1, 0.96]
    )

    plt.savefig(
        chart_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    # =====================================================
    # Build PDF
    # =====================================================

    doc = SimpleDocTemplate(
        TEST_RESULT_PATH,
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    normal_style = styles["BodyText"]
    normal_style.wordWrap = "CJK"

    normal_style.fontName = "NotoSans"
    normal_style.leading = 18

    title_style = styles["Title"]

    title_style.fontName = "NotoSans"

    story = []

    # Title
    story.append(
        Paragraph(
            "Vietnamese Sentiment API - Enterprise QA Report",
            title_style
        )
    )

    story.append(
        Spacer(1, 20)
    )

    # Summary
    pass_rate = (
        (passed / total) * 100
        if total > 0
        else 0
    )

    summary_text = f"""
    <b>Total Test Cases:</b> {total}<br/>
    <b>Passed:</b> {passed}<br/>
    <b>Failed:</b> {failed}<br/>
    <b>Skipped:</b> {skipped}<br/>
    <b>Pass Rate:</b> {pass_rate:.2f}%<br/>
    <b>Generated At:</b> {datetime.now()}<br/>
    <b>Environment:</b> github.dev / Codespaces<br/>
    <b>Base URL:</b> {BASE_URL}<br/>
    """

    story.append(
        Paragraph(
            summary_text,
            normal_style
        )
    )

    story.append(
        Spacer(1, 20)
    )

    # Add chart image
    story.append(
        Image(
            chart_path,
            width=500,
            height=350
        )
    )

    story.append(
        Spacer(1, 20)
    )

    # Failed categories
    failed_category_text = "\n".join(
        [
            f"{k}: {v}"
            for k, v in failed_category_counter.items()
        ]
    )

    story.append(
        Paragraph(
            "<b>Failed Categories</b>",
            normal_style
        )
    )

    story.append(
        Preformatted(
            failed_category_text,
            normal_style
        )
    )

    story.append(
        Spacer(1, 20)
    )

    # =====================================================
    # Detailed Logs
    # =====================================================

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "<b>Detailed Test Logs</b>",
            normal_style
        )
    )

    story.append(
        Spacer(1, 12)
    )

    detailed_logs = ""

    for r in failed_results:

        detailed_logs += (
            f"TC ID      : {r['tc_id']}\n"
            f"Category   : {r['category']}\n"
            f"Status     : {r['status']}\n"
            f"Error      : {r.get('error', '')}\n"
            f"\n"
        )

    story.append(
        Preformatted(
            detailed_logs,
            normal_style,
            maxLineLength=100
        )
    )

    # =====================================================
    # Export PDF
    # =====================================================

    doc.build(story)

    # Cleanup
    if os.path.exists(chart_path):
        os.remove(chart_path)

    print(
        f"\nPDF report exported: {TEST_RESULT_PATH}"
    )
# =========================================================
# Auto Generate Report
# =========================================================

@pytest.fixture(scope="session", autouse=True)
def generate_report_after_tests(request):

    yield

    generate_test_report(
        TEST_RESULTS
    )

    print(
        f"\nReport generated: {TEST_RESULT_PATH}"
    )
def test_vietnamese_text(page: Page):

    page.goto("http://localhost:8502")

    # page.get_by_role("textbox").fill(
    #     "sản phẩm rất tốt"
    # )

    # page.get_by_role(
    #     "button",
    #     name="Predict"
    # ).click()

    # expect = page.locator("text=positive")

    # assert expect.is_visible()
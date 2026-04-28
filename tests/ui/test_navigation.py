
import pytest


@pytest.mark.testcase("UI005")
def test_homepage_navigation(pages, ui_base_url):

    pages.home.open()
    pages.home.page.wait_for_load_state("networkidle")

    assert pages.home.page.url.startswith(ui_base_url)

    assert pages.home.search_input.is_visible()

    assert "Dog Tree" in pages.home.page.title()

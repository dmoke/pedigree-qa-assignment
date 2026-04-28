import pytest


class TestSearch:

    @pytest.mark.testcase("UI006")
    def test_search_changes_results(self, pages):
        home = pages.home

        home.open()
        home.page.wait_for_load_state("networkidle")

        initial_count = home.get_visible_dog_count()
        assert initial_count > 0

        query = "Max"
        home.search(query)

        home.page.wait_for_load_state("networkidle")

        assert home.get_search_value() == query

        filtered_count = home.get_visible_dog_count()
        assert filtered_count <= initial_count
        assert filtered_count > 0

        assert query.lower() in home.dog_list.first.inner_text().lower()

    @pytest.mark.testcase("UI007")
    def test_search_reduces_results(self, pages):
        home = pages.home

        home.open()
        home.page.wait_for_load_state("networkidle")

        initial_count = home.get_visible_dog_count()
        assert initial_count > 0

        home.search("Max")
        home.page.wait_for_load_state("networkidle")
        count_max = home.get_visible_dog_count()

        home.search("M")
        home.page.wait_for_load_state("networkidle")
        count_m = home.get_visible_dog_count()

        assert count_max <= initial_count
        assert count_m >= count_max

    @pytest.mark.testcase("UI008")
    def test_search_case_insensitive(self, pages):
        home = pages.home

        home.open()
        home.page.wait_for_load_state("networkidle")

        home.search("max")
        home.page.wait_for_load_state("networkidle")
        count_lower = home.get_visible_dog_count()

        home.search("MAX")
        home.page.wait_for_load_state("networkidle")
        count_upper = home.get_visible_dog_count()

        assert count_lower == count_upper

    @pytest.mark.testcase("UI009")
    def test_search_clear_restores_results(self, pages):
        home = pages.home

        home.open()
        home.page.wait_for_load_state("networkidle")

        initial_count = home.get_visible_dog_count()

        home.search("Max")
        home.page.wait_for_load_state("networkidle")

        filtered_count = home.get_visible_dog_count()
        assert filtered_count <= initial_count

        home.clear_search()
        home.page.wait_for_load_state("networkidle")

        restored_count = home.get_visible_dog_count()
        assert restored_count == initial_count

    @pytest.mark.testcase("UI010")
    def test_search_no_results(self, pages):
        home = pages.home

        home.open()
        home.page.wait_for_load_state("networkidle")

        home.search("zzzz_nonexistent")

        assert home.get_visible_dog_count() == 0

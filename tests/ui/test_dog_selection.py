import pytest

from pages.index import Pages


class TestDogSelection:
    @pytest.mark.testcase("UI001")
    def test_dog_selection_updates_left_panel(self, pages):
        home = pages.home

        home.open()
        home.page.wait_for_load_state("networkidle")

        first_dog = home.dog_list.first
        dog_text = first_dog.inner_text()

        first_dog.click()

        home.page.wait_for_load_state("networkidle")

        assert home.get_selected_dog_name() in dog_text

    @pytest.mark.testcase("UI002")
    def test_different_dog_updates_selection(self, pages):
        home = pages.home

        home.open()
        home.page.wait_for_load_state("networkidle")

        first_dog = home.dog_list.first
        first_dog.click()
        home.wait_for_selection()
        first_id = home.get_selected_dog_id()

        second_dog = home.dog_list.nth(2)
        second_dog.scroll_into_view_if_needed()
        second_dog.click()
        home.wait_for_selection()
        second_id = home.get_selected_dog_id()

        assert first_id != second_id

    @pytest.mark.testcase("UI003")
    def test_dog_selection_updates_tree(self, pages):
        home = pages.home

        home.open()
        home.page.wait_for_load_state("networkidle")

        dog = home.dog_card(143)

        dog.click()

        home.wait_for_selection()

        tree_node = home.tree_node("77")
        tree_node.wait_for(state="visible")

        assert tree_node.is_visible()

    @pytest.mark.testcase("UI004")
    def test_reselect_same_dog_keeps_state(self, pages):
        home = pages.home

        home.open()
        home.page.wait_for_load_state("networkidle")

        dog = home.dog_list.first
        dog_text = dog.inner_text()

        dog.click()
        first_name = home.get_selected_dog_name()

        dog.click()
        second_name = home.get_selected_dog_name()

        assert first_name == second_name
        assert first_name in dog_text

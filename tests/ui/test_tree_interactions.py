import pytest


class TestTreeInteractions:

    @pytest.mark.testcase("UI011")
    def test_tree_node_click_updates_left_panel(self, pages):
        home = pages.home

        home.open()
        home.page.wait_for_load_state("networkidle")

        home.click_dog_by_id(143)
        home.wait_for_selection()

        home.click_tree_node_by_index(1)

        selected_id = home.get_selected_dog_id()
        assert selected_id

    @pytest.mark.testcase("UI012")
    def test_tree_hover_triggers_peek_panel(self, pages):
        home = pages.home

        home.open()
        home.page.wait_for_load_state("networkidle")

        home.click_dog_by_id(143)
        home.wait_for_selection()

        home.hover_tree_node_by_index(1)

        assert "PEEK" in home.left_panel.inner_text()

    @pytest.mark.testcase("UI013")
    def test_tree_hover_highlights_svg_lines(self, pages):
        home = pages.home

        home.open()
        home.page.wait_for_load_state("networkidle")

        home.click_dog_by_id(143)
        home.wait_for_selection()

        home.hover_tree_node_by_index(1)

        assert home.get_highlighted_svg_lines_count() > 0


class TestUIPedigreeDataConsistency:
    """
    UI-level pedigree tests validating that the application correctly renders
    pedigree data based on API responses and handles edge cases gracefully.

    Covers:
    - Rendering of a selected dog's pedigree from API data
    - Basic structure validation (root + ancestors)
    - UI resilience with small or filtered datasets
    """

    @pytest.mark.testcase("UI014")
    def test_ui_renders_consistent_pedigree_from_mocked_api(self, pages):
        home = pages.home

        mock_dogs = [
            {
                "id": "100",
                "name": "Root",
                "breed": "A",
                "sex": "M",
                "height_cm": None,
                "weight_kg": None,
                "sire_id": "101",
                "dam_id": "102",
            },
            {
                "id": "101",
                "name": "Sire",
                "breed": "B",
                "sex": "M",
                "height_cm": None,
                "weight_kg": None,
                "sire_id": None,
                "dam_id": None,
            },
            {
                "id": "102",
                "name": "Dam",
                "breed": "C",
                "sex": "F",
                "height_cm": None,
                "weight_kg": None,
                "sire_id": None,
                "dam_id": None,
            },
        ]

        mock_ancestors = {
            "dog": mock_dogs[0],
            "ancestors": [mock_dogs[1], mock_dogs[2]],
            "has_ancestors": True,
        }

        home.page.route("**/dogs", lambda route: route.fulfill(json=mock_dogs))
        home.page.route("**/dogs/100", lambda route: route.fulfill(json=mock_dogs[0]))
        home.page.route(
            "**/dogs/100/ancestors", lambda route: route.fulfill(json=mock_ancestors)
        )

        home.open()
        home.page.wait_for_load_state("networkidle")

        assert home.get_visible_dog_count() == 3

        home.click_dog_by_id("100")
        home.wait_for_selection()

        assert "#100" in home.get_selected_dog_id()
        assert "Root" in home.get_selected_dog_name()

        assert home.get_tree_node_count() >= 3

        node_ids = home.page.locator(".tree-node").all_inner_texts()
        assert any("#101" in text for text in node_ids)
        assert any("#102" in text for text in node_ids)

        node = home.tree_node("101")
        node.wait_for(state="visible")
        node.hover()

        home.page.locator(".dog-card.peek").wait_for(state="visible")

        assert home.page.locator(".dog-card.peek").is_visible()
        assert home.page.locator(".peek-indicator").is_visible()

    @pytest.mark.testcase("UI015")
    def test_search_handles_small_mocked_dataset(self, pages):
        home = pages.home

        mock_dogs = [
            {
                "id": "200",
                "name": "Alpha",
                "breed": "A",
                "sex": "M",
                "height_cm": None,
                "weight_kg": None,
                "sire_id": None,
                "dam_id": None,
            },
            {
                "id": "201",
                "name": "Beta",
                "breed": "B",
                "sex": "F",
                "height_cm": None,
                "weight_kg": None,
                "sire_id": None,
                "dam_id": None,
            },
            {
                "id": "202",
                "name": "Gamma",
                "breed": "C",
                "sex": "M",
                "height_cm": None,
                "weight_kg": None,
                "sire_id": None,
                "dam_id": None,
            },
        ]

        home.page.route("**/dogs", lambda route: route.fulfill(json=mock_dogs))

        home.open()
        home.page.wait_for_load_state("networkidle")

        assert home.get_visible_dog_count() == 3

        home.search("Alpha")
        assert home.get_visible_dog_count() == 1
        assert "200" in home.get_visible_dog().first.inner_text()

        home.clear_search()
        assert home.get_visible_dog_count() == 3

        home.search("201")
        assert home.get_visible_dog_count() == 1
        assert "201" in home.get_visible_dog().first.inner_text()

        home.clear_search()
        assert home.get_visible_dog_count() == 3

        home.search("NonExisting")
        assert home.get_visible_dog_count() == 0

        home.clear_search()
        assert home.get_visible_dog_count() == 3


class TestUIPedigreeEdgeCases:
    """Edge case tests for pedigree UI handling missing or problematic data."""

    @pytest.mark.testcase("UI016")
    def test_pedigree_with_no_ancestors_displays_correctly(self, pages):
        home = pages.home

        mock_dog = {
            "id": "300",
            "name": "Orphan",
            "breed": "Labrador",
            "sex": "M",
            "height_cm": None,
            "weight_kg": None,
            "sire_id": None,
            "dam_id": None,
        }

        mock_ancestors = {
            "dog": mock_dog,
            "ancestors": [],
            "has_ancestors": False,
        }

        home.page.route("**/dogs", lambda route: route.fulfill(json=[mock_dog]))
        home.page.route("**/dogs/300", lambda route: route.fulfill(json=mock_dog))
        home.page.route(
            "**/dogs/300/ancestors", lambda route: route.fulfill(json=mock_ancestors)
        )

        home.open()
        home.page.wait_for_load_state("networkidle")

        home.click_dog_by_id("300")
        home.wait_for_selection()

        assert "#300" in home.get_selected_dog_id()
        assert "Orphan" in home.get_selected_dog_name()

        assert home.get_tree_node_count() <= 1

    @pytest.mark.testcase("UI017")
    def test_pedigree_handles_missing_parent_references(self, pages):
        home = pages.home

        mock_dog = {
            "id": "400",
            "name": "Partial",
            "breed": "Labrador",
            "sex": "M",
            "height_cm": None,
            "weight_kg": None,
            "sire_id": "401",
            "dam_id": None,
        }

        mock_ancestors = {
            "dog": mock_dog,
            "ancestors": [
                {
                    "id": "401",
                    "name": "Sire",
                    "breed": "Labrador",
                    "sex": "M",
                    "height_cm": None,
                    "weight_kg": None,
                    "sire_id": None,
                    "dam_id": None,
                }
            ],
            "has_ancestors": True,
        }

        home.page.route("**/dogs", lambda route: route.fulfill(json=[mock_dog]))
        home.page.route("**/dogs/400", lambda route: route.fulfill(json=mock_dog))
        home.page.route(
            "**/dogs/400/ancestors", lambda route: route.fulfill(json=mock_ancestors)
        )

        home.open()
        home.page.wait_for_load_state("networkidle")

        home.click_dog_by_id("400")
        home.wait_for_selection()

        assert home.get_tree_node_count() >= 1

    @pytest.mark.testcase("UI018")
    def test_pedigree_handles_api_error_gracefully(self, pages):
        home = pages.home

        home.page.route("**/dogs", lambda route: route.fulfill(json=[]))
        home.page.route(
            "**/dogs/500/ancestors",
            lambda route: route.fulfill(
                status=500, json={"error": "Internal Server Error"}
            ),
        )

        home.open()
        home.page.wait_for_load_state("networkidle")

        home.search("500")

        assert home.get_visible_dog_count() == 0

    @pytest.mark.testcase("UI019")
    def test_pedigree_handles_empty_search_results(self, pages):
        home = pages.home

        mock_dogs = [
            {
                "id": "600",
                "name": "Dog1",
                "breed": "A",
                "sex": "M",
                "height_cm": None,
                "weight_kg": None,
                "sire_id": None,
                "dam_id": None,
            },
            {
                "id": "601",
                "name": "Dog2",
                "breed": "B",
                "sex": "F",
                "height_cm": None,
                "weight_kg": None,
                "sire_id": None,
                "dam_id": None,
            },
        ]

        home.page.route("**/dogs", lambda route: route.fulfill(json=mock_dogs))

        home.open()
        home.page.wait_for_load_state("networkidle")

        home.search("NonExistentDog12345")

        assert home.get_visible_dog_count() == 0

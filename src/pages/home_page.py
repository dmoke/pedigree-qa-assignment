from typing import Self

from playwright.sync_api import Page, Locator

from pages.base_page import BasePage
from utils.decorators import step


class HomePage(BasePage):
    path = "/"

    dog_list: Locator
    search_input: Locator
    search_clear: Locator
    left_panel: Locator
    tree: Locator

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)

        self.dog_list = page.locator(".dog-list-card")
        self.search_input = page.locator("#search-input")
        self.search_clear = page.locator("#search-clear")

        self.left_panel = page.locator("#left-panel")
        self.tree = page.locator(".tree-node")

    @step
    def open(self) -> Self:
        return self.navigate()

    @step
    def dog_card(self, dog_id: str) -> Locator:
        return self.dog_list.filter(has_text=f"#{dog_id}")

    @step
    def tree_node(self, dog_id: str) -> Locator:
        return self.page.locator(f".tree-node[data-node-id='{dog_id}']")

    @step
    def click_dog_by_id(self, dog_id: str) -> Self:
        self.dog_card(dog_id).click()
        return self

    @step
    def get_visible_dog_count(self) -> int:
        return self.page.locator(".dog-list-card:visible").count()

    @step
    def get_hidden_dog_count(self) -> int:
        return self.page.locator(".dog-list-card:hidden").count()

    @step
    def search(self, text: str) -> Self:
        self.search_input.fill(text)
        self.search_input.press("Enter")
        return self

    @step
    def clear_search(self) -> Self:
        self.search_clear.click()
        return self

    @step
    def get_search_value(self) -> str:
        return self.search_input.input_value()

    @step
    def get_selected_dog_id(self) -> str:
        return self.left_panel.locator(".dog-card__id").inner_text()

    @step
    def get_selected_dog_name(self) -> str:
        return self.left_panel.locator(".dog-card__name").inner_text()

    @step
    def get_selected_dog_breed(self) -> str:
        return self.left_panel.locator(".dog-card__value").first.inner_text()

    @step
    def click_tree_node(self, dog_id: str) -> Self:
        self.tree_node(dog_id).click()
        return self

    @step
    def hover_tree_node(self, dog_id: str) -> Self:
        self.tree_node(dog_id).hover()
        return self

    @step
    def get_tree_node_count(self) -> int:
        return self.tree.count()

    @step
    def is_loaded(self) -> bool:
        return self.dog_list.first.is_visible()

    @step
    def get_visible_dog(self) -> Locator:
        return self.page.locator(".dog-list-card:visible")

    @step
    def get_hidden_dog(self) -> Locator:
        return self.page.locator(".dog-list-card:hidden")

    @step
    def wait_for_selection(self) -> Self:
        self.page.wait_for_timeout(500)
        self.left_panel.locator(".dog-card__name").wait_for(state="visible")
        self.left_panel.locator(".dog-card__id").wait_for(state="visible")
        return self

    @step
    def get_tree_nodes(self) -> Locator:
        return self.page.locator(".tree-node:not(.root)")

    @step
    def get_tree_node_by_index(self, index: int) -> Locator:
        return self.get_tree_nodes().nth(index)

    @step
    def hover_tree_node_by_index(self, index: int) -> Self:
        self.get_tree_node_by_index(index).hover()
        return self

    @step
    def click_tree_node_by_index(self, index: int) -> Self:
        self.get_tree_node_by_index(index).click()
        return self

    @step
    def get_highlighted_svg_lines_count(self) -> int:
        return self.page.locator("svg line.highlight").count()

    @step
    def get_faded_svg_lines_count(self) -> int:
        return self.page.locator("svg line.faded").count()

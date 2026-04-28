

from pages.home_page import HomePage


class Pages:
    def __init__(self, page, base_url):
        self.home: HomePage = HomePage(page, base_url)
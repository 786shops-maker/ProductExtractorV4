"""
html_cleaner.py

Clean HTML before parsing.
"""

from bs4 import BeautifulSoup
import re


class HTMLCleaner:

    def clean(self, html: str) -> BeautifulSoup:
        """
        Returns a cleaned BeautifulSoup object.
        """

        soup = BeautifulSoup(html, "lxml")

        self.remove_scripts(soup)
        self.remove_styles(soup)
        self.remove_comments(soup)
        self.remove_hidden(soup)

        return soup

    # -------------------------------------------------

    def remove_scripts(self, soup):

        for tag in soup(["script", "noscript"]):
            tag.decompose()

    # -------------------------------------------------

    def remove_styles(self, soup):

        for tag in soup(["style"]):
            tag.decompose()

    # -------------------------------------------------

    def remove_comments(self, soup):

        comments = soup.find_all(
            string=lambda text:
            text and "<!--" in str(text)
        )

        for c in comments:
            c.extract()

    # -------------------------------------------------

    def remove_hidden(self, soup):

        hidden = soup.select(
            '[style*="display:none"],'
            '[style*="display: none"],'
            '[hidden],'
            '.hidden'
        )

        for tag in hidden:
            tag.decompose()

    # -------------------------------------------------

    def text(self, html):

        soup = self.clean(html)

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text

    # -------------------------------------------------

    def title(self, html):

        soup = self.clean(html)

        if soup.title:
            return soup.title.text.strip()

        return ""
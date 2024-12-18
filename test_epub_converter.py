import unittest
from epub_converter import EpubConverter
from ebooklib import epub
import os
import re


def _generate_epub_element(title: str, file_name: str, lang: str, content: str) -> epub.EpubHtml:
    element = epub.EpubHtml(title=title, file_name=file_name, lang=lang)
    element.content = content
    return element


class TestEpubConverter(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Create a minimal EPUB file for testing
        book = epub.EpubBook()
        book.set_title("Test Book")
        book.set_language("en")

        # Chapter 1
        c1 = _generate_epub_element(
            "Chapter 1",
            "chap_01.xhtml",
            "en",
            "<h1>Chapter 1</h1><p>Content of Chapter 1.</p>",
        )

        # Section 1.1
        c1_1 = _generate_epub_element(
            "Section 1.1",
            "chap_01_1.xhtml",
            "en",
            "<h2>Section 1.1</h2><p>Content of Section 1.1.</p>",
        )

        # Chapter 2
        c2 = _generate_epub_element(
            "Chapter 2",
            "chap_02.xhtml",
            "en",
            "<h1>Chapter 2</h1><p>Content of Chapter 2.</p>",
        )

        for item in [c1, c1_1, c2]:
            book.add_item(item)

        # Define Table of Contents
        book.toc = [
            (
                epub.Section('Chapter 1'),
                [
                    epub.Link('chap_01.xhtml', 'Chapter 1', 'chap_01'),
                    (
                        epub.Section('Section 1.1'),
                        [epub.Link('chap_01_1.xhtml', 'Section 1.1', 'chap_01_1')]
                    )
                ]
            ),
            epub.Link('chap_02.xhtml', 'Chapter 2', 'chap_02')
        ]

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        epub.write_epub("test.epub", book)

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove("test.epub")

    def test_convert_returns_dict(self) -> None:
        converter = EpubConverter()
        result = converter.convert("test.epub")
        self.assertIsInstance(result, dict)

    def test_convert_extracts_chapter_titles(self) -> None:
        converter = EpubConverter()
        result = converter.convert("test.epub")
        expected_chapters = ["Chapter 1", "Chapter 2"]
        for chapter in expected_chapters:
            self.assertIn(chapter, result)

    def test_convert_extracts_chapter_content(self) -> None:
        converter = EpubConverter()
        result = converter.convert("test.epub")
        chapter_content = result["Chapter 1"]["content"]
        self.assertIn("Content of Chapter 1.", chapter_content)

    def test_convert_extracts_subsection_titles(self) -> None:
        converter = EpubConverter()
        result = converter.convert("test.epub")
        self.assertIn("Section 1.1", result["Chapter 1"])

    def test_convert_extracts_subsection_content(self) -> None:
        converter = EpubConverter()
        result = converter.convert("test.epub")
        subsection_content = result["Chapter 1"]["Section 1.1"]["content"]
        self.assertIn("Content of Section 1.1.", subsection_content)

    def test_content_is_plain_text(self) -> None:
        converter = EpubConverter()
        result = converter.convert("test.epub")
        chapter_content = result["Chapter 1"]["content"]
        self.assertFalse(
            self._contains_html_tags(chapter_content), "Content contains HTML tags"
        )

    def _contains_html_tags(self, text: str) -> bool:
        return bool(re.search(r"<[^>]+>", text))


if __name__ == "__main__":
    unittest.main()

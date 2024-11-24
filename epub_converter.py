from typing import Any, Dict, List, Tuple, Union
from ebooklib import epub
from bs4 import BeautifulSoup

class EpubConverter:
    def convert(self, epub_file: str) -> Dict[str, Any]:
        self.book = epub.read_epub(epub_file)
        return self._build_subsection_structure(self.book.toc)

    def _build_subsection_structure(self, toc: List[Union[epub.Link, Tuple[epub.Section, List[Any]]]]) -> Dict[str, Any]:
        structure: Dict[str, Any] = {}
        for item in toc:
            self._process_toc_item(item, structure)
        return structure

    def _process_toc_item(
        self, item: Union[epub.Link, Tuple[epub.Section, List[Any]]], structure: Dict[str, Any]
    ) -> None:
        if self._is_epub_link(item):
            self._add_link_content(item, structure)
        elif self._is_section(item):
            self._add_section_content(item, structure)

    def _is_epub_link(self, item: Union[epub.Link, Tuple[epub.Section, List[Any]]]) -> bool:
        return isinstance(item, epub.Link)

    def _is_section(self, item: Union[epub.Link, Tuple[epub.Section, List[Any]]]) -> bool:
        return isinstance(item, tuple)

    def _add_link_content(
        self, link_item: epub.Link, structure: Dict[str, Any]
    ) -> None:
        title = link_item.title
        content = self._extract_plain_text(link_item.href)
        structure[title] = {"content": content}

    def _extract_section_title(self, section_item: Tuple[epub.Section, List[Any]]) -> str:
        return section_item[0].title

    def _extract_subsections_from_section(
        self, section_item: Tuple[epub.Section, List[Any]]
    ) -> List[Union[epub.Link, Tuple[epub.Section, List[Any]]]]:
        return section_item[1]

    def _add_section_content(
        self, section_item: Tuple[epub.Section, List[Any]], structure: Dict[str, Any]
    ) -> None:
        section_title = self._extract_section_title(section_item)
        subsections = self._extract_subsections_from_section(section_item)
        subsection_structure = self._build_subsection_structure(subsections)
        structure[section_title] = subsection_structure

    def _extract_plain_text(self, href: str) -> str:
        html_content = self._get_document_content(href)
        return self._parse_plain_text_from_html(html_content)

    def _get_document_content(self, href: str) -> Union[Any, str]:
        document = self.book.get_item_with_href(href)
        if document:
            return document.get_content().decode("utf-8")
        return ""

    def _parse_plain_text_from_html(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator="\n").strip()

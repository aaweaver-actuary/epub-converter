from typing import Any, Dict, List, Tuple, Union
from ebooklib import epub
from bs4 import BeautifulSoup
from functools import wraps

EpubLink = epub.Link
EpubSection = epub.Section
EpubSectionWithSubsections = Tuple[
    EpubSection, List[Union[EpubLink, Tuple[EpubSection, List[Any]]]]
]
EpubTocItem = Union[EpubLink, EpubSectionWithSubsections]
EpubToc = List[EpubTocItem]
EpubStructure = Dict[str, Any]


def log_on_exception(message: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise Exception(f"{message}: {e}")

        return wrapper

    return decorator


class EpubConverter:
    def __init__(self, epub_file: str) -> None:
        self.epub_file = epub_file
        self.book = epub.read_epub(epub_file)

    def convert(self, epub_file: str) -> EpubStructure:
        return self._build_subsection_structure(self.book.toc)

    def _build_subsection_structure(self, toc: EpubToc) -> EpubStructure:
        structure = self._initialize_section_structure()
        return self._process_toc_items(toc, structure)

    def _initialize_section_structure(self) -> EpubStructure:
        return {}

    def _process_toc_items(
        self, toc: EpubToc, structure: EpubStructure
    ) -> EpubStructure:
        for item in toc:
            self._process_toc_item(item, structure)
        return structure

    def _process_toc_item(self, item: EpubTocItem, structure: EpubStructure) -> None:
        if self._is_item_of_type_epub_link(item):
            self._add_link_content_to_structure(item, structure)
        elif self._is_item_of_type_section(item):
            self._add_section_content_to_structure(item, structure)

    def _is_item_of_type_epub_link(self, item: EpubTocItem) -> bool:
        return isinstance(item, epub.Link)

    def _is_item_of_type_section(self, item: EpubTocItem) -> bool:
        return isinstance(item, tuple)

    def _add_link_content_to_structure(
        self, link_item: EpubLink, structure: EpubStructure
    ) -> None:
        title = link_item.title
        content = self._get_plain_text_from_html(link_item.href)
        structure[title] = {"content": content}

    def _get_section_title(
        self, section_item: EpubSectionWithSubsections
    ) -> Union[str, Any]:
        return section_item[0].title

    def _get_subsections_from_section(
        self, section_item: EpubSectionWithSubsections
    ) -> EpubToc:
        return section_item[1]

    def _add_section_content_to_structure(
        self, section_item: EpubSectionWithSubsections, structure: EpubStructure
    ) -> None:
        section_structure = self._initialize_section_structure()

        if self._has_link_to_content(section_item):
            section_structure["content"] = self._get_plain_text_from_html(
                section_item[0].href
            )

        self._build_subsections_recursively(section_structure, section_item)

        structure[self._get_section_title(section_item)] = section_structure

    def _has_link_to_content(self, section_item: EpubSectionWithSubsections) -> bool:
        return hasattr(section_item[0], "href") and section_item[0].href

    def _build_subsections_recursively(
        self,
        section_structure: Dict[str, Any],
        section_item: Tuple[epub.Section, List[Any]],
    ) -> None:
        return section_structure.update(
            self._build_subsection_structure(
                self._get_subsections_from_section(section_item)
            )
        )

    def _get_plain_text_from_html(self, href: str) -> str:
        html_content = self._get_document_content(href)
        return self._parse_plain_text_from_html(html_content)

    @log_on_exception("in method _get_document_content")
    def _get_document_content(self, href: str) -> Union[Any, str]:
        document = self.book.get_item_with_href(href)
        if document:
            return document.get_content().decode("utf-8")

    def _parse_plain_text_from_html(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator="\n").strip()

import pytest
from epub_converter import EpubConverter


@pytest.fixture
def mocked_document_content(mocker):
    return mocker.patch("epub_converter.EpubConverter._get_document_content")


def test__get_document_content(mocked_document_content):
    ec = EpubConverter()

    html = '<a href="content.html">'
    href = "content.html"
    mocked_document_content.return_value = html

    assert (
        ec._get_plain_text_from_html(href) == html
    ), f"Expected {html} to be returned, but got {ec._get_plain_text_from_html(href)}"

from schemas.page_reader_result import PageReaderResult
from schemas.page import Page
from schemas.source import Source

class PageReaderNode:
    def __init__(self, reader):
        self.reader = reader

    def run(self, sources: list[Source]) -> PageReaderResult:
        pages = []
        failed_sources = []
        for source in sources:
            data = self.reader.read(source.url)
            if data['success']:
                pages.append(
                    Page(
                        url = source.url,
                        content = data['content'],
                        title = data['title']
                    )
                )

            else:
                failed_sources.append(source)
        
        return PageReaderResult(pages = pages, failed_sources = failed_sources)
        
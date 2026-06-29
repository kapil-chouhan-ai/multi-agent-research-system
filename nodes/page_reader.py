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
            if data['success'] :
                if len(data['content'].strip()) > 500:
                    pages.append(
                        Page(
                            url = source.url,
                            content = data['content'][:60000],
                            title = data['title']
                        )
                    )
            else:
                failed_sources.append(source)

        # print(f"{len(pages) = }\n")
        return PageReaderResult(pages = pages, failed_sources = failed_sources)
        
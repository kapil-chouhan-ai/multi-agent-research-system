from schemas.page import Page
from schemas.chunk import Chunk
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChunkingNode:

    def __init__(self, chunk_size = 500, chunk_overlap = 50):
        self.splitter = RecursiveCharacterTextSplitter(chunk_size= chunk_size,
                                                       chunk_overlap = chunk_overlap)

    def run(self, pages: list[Page]) -> list[Chunk]:
        chunks = []
        
        for page_idx, page in enumerate(pages, start = 1):
            texts = self.splitter.split_text(page.content)

            for chunk_idx, chunk in enumerate(texts, start = 1):
                chunks.append(Chunk(
                    content = chunk,
                    chunk_id = f"page_{page_idx}_chunk_{chunk_idx}",
                    url = page.url
                ))
        
        return chunks
        

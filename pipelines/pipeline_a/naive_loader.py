import re
from pathlib import Path
from typing import List, Dict, Any

class NaiveDocumentLoader:
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_document(self, file_path: Path) -> List[Dict[str, Any]]:
        text = file_path.read_text(encoding="utf-8")
        doc_id = file_path.stem

        pages = re.split(r"--- PAGE (\d+) ---", text)
        chunks = []
        global_chunk_idx = 0

        if len(pages) > 1:
            current_page = 1
            for i in range(1, len(pages), 2):
                page_num = int(pages[i])
                page_content = pages[i+1] if (i+1) < len(pages) else ""
                page_chunks = self._chunk_text(page_content, doc_id, page_num, global_chunk_idx)
                chunks.extend(page_chunks)
                global_chunk_idx += len(page_chunks)
        else:
            chunks = self._chunk_text(text, doc_id, 1, 0)

        return chunks

    def _chunk_text(self, text: str, doc_id: str, page_num: int, start_idx: int) -> List[Dict[str, Any]]:
        clean_text = text.strip()
        chunks = []
        idx = start_idx
        start = 0

        while start < len(clean_text):
            end = min(start + self.chunk_size, len(clean_text))
            chunk_slice = clean_text[start:end]

            chunks.append({
                "chunk_id": f"{doc_id}_P{page_num}_C{idx:03d}",
                "doc_id": doc_id,
                "page_number": page_num,
                "content": chunk_slice,
                "start_char": start,
                "end_char": end,
                "pipeline": "pipeline_a"
            })
            idx += 1
            start += (self.chunk_size - self.chunk_overlap)
            if start >= len(clean_text) - 10:
                break

        return chunks

    def load_corpus(self, corpus_dir: Path) -> List[Dict[str, Any]]:
        all_chunks = []
        for file_path in sorted(corpus_dir.glob("*.md")):
            chunks = self.load_document(file_path)
            all_chunks.extend(chunks)
        return all_chunks

if __name__ == "__main__":
    loader = NaiveDocumentLoader()
    corpus = loader.load_corpus(Path("data/corpus"))
    print(f"Loaded {len(corpus)} naive chunks from corpus.")
    if corpus:
        print(f"Sample chunk: {corpus[0]['chunk_id']} (Page {corpus[0]['page_number']}): {corpus[0]['content'][:100]}...")


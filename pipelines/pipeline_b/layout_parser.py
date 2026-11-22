import re
from pathlib import Path
from typing import List, Dict, Any, Optional

class TableCell(Dict):
    pass

class ExtractedTable:
    def __init__(self, table_id: str, title: str, headers: List[str], rows: List[List[str]], doc_id: str, page_number: int, metadata_lines: Optional[List[str]] = None):
        self.table_id = table_id
        self.title = title
        self.headers = [h.strip() for h in headers]
        self.rows = [[c.strip() for c in r] for r in rows]
        self.doc_id = doc_id
        self.page_number = page_number
        self.metadata_lines = metadata_lines or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table_id": self.table_id,
            "title": self.title,
            "metadata": self.metadata_lines,
            "headers": self.headers,
            "rows": self.rows,
            "row_count": len(self.rows),
            "doc_id": self.doc_id,
            "page_number": self.page_number
        }

    def to_markdown(self) -> str:
        header_line = "| " + " | ".join(self.headers) + " |"
        sep_line = "| " + " | ".join(["---"] * len(self.headers)) + " |"
        row_lines = ["| " + " | ".join(r) + " |" for r in self.rows]
        meta_str = "\n".join(self.metadata_lines) + "\n" if self.metadata_lines else ""
        return f"### {self.title}\n{meta_str}" + "\n".join([header_line, sep_line] + row_lines)

    def find_cell(self, row_filter_key: str, target_col: str) -> Optional[str]:
        target_col_idx = -1
        for idx, h in enumerate(self.headers):
            if target_col.lower() in h.lower():
                target_col_idx = idx
                break
        if target_col_idx == -1:
            return None

        for row in self.rows:
            row_str = " ".join(row).lower()
            if row_filter_key.lower() in row_str:
                return row[target_col_idx]
        return None

class LayoutAwareParser:
    
    def __init__(self):
        pass

    def parse_document(self, file_path: Path) -> Dict[str, Any]:
        text = file_path.read_text(encoding="utf-8")
        doc_id = file_path.stem

        pages_raw = re.split(r"--- PAGE (\d+) ---", text)
        sections = []
        tables = []

        if len(pages_raw) > 1:
            for i in range(1, len(pages_raw), 2):
                page_num = int(pages_raw[i])
                page_content = pages_raw[i+1] if (i+1) < len(pages_raw) else ""
                parsed_page = self._parse_page_content(page_content, doc_id, page_num)
                sections.extend(parsed_page["sections"])
                tables.extend(parsed_page["tables"])
        else:
            parsed_page = self._parse_page_content(text, doc_id, 1)
            sections.extend(parsed_page["sections"])
            tables.extend(parsed_page["tables"])

        return {
            "doc_id": doc_id,
            "sections": sections,
            "tables": tables,
            "total_pages": max([s["page_number"] for s in sections], default=1)
        }

    def _parse_page_content(self, page_text: str, doc_id: str, page_num: int) -> Dict[str, Any]:
        sections = []
        tables = []

        table_pattern = re.compile(
            r"(Table\s+\d+:\s*[^\n]+)\n([\s\S]*?)(\|[\s\S]+?)(?=\n\n|\n\[|\Z)",
            re.MULTILINE
        )

        last_end = 0
        table_matches = list(table_pattern.finditer(page_text))

        if table_matches:
            for match in table_matches:
                pre_text = page_text[last_end:match.start()].strip()
                if pre_text:
                    sections.append({
                        "doc_id": doc_id,
                        "page_number": page_num,
                        "type": "narrative_text",
                        "content": pre_text
                    })

                table_title = match.group(1).strip()
                intervening_meta = match.group(2).strip()
                table_body = match.group(3).strip()
                
                meta_lines = [l.strip() for l in intervening_meta.split("\n") if l.strip()] if intervening_meta else []

                parsed_table = self._parse_markdown_table(table_title, table_body, doc_id, page_num, meta_lines)
                if parsed_table:
                    tables.append(parsed_table)
                    sections.append({
                        "doc_id": doc_id,
                        "page_number": page_num,
                        "type": "structured_table",
                        "table_id": parsed_table.table_id,
                        "content": parsed_table.to_markdown(),
                        "table_object": parsed_table
                    })
                last_end = match.end()

            post_text = page_text[last_end:].strip()
            if post_text:
                sections.append({
                    "doc_id": doc_id,
                    "page_number": page_num,
                    "type": "narrative_text",
                    "content": post_text
                })
        else:
            if page_text.strip():
                sections.append({
                    "doc_id": doc_id,
                    "page_number": page_num,
                    "type": "narrative_text",
                    "content": page_text.strip()
                })

        return {"sections": sections, "tables": tables}

    def _parse_markdown_table(self, title: str, table_str: str, doc_id: str, page_num: int, meta_lines: Optional[List[str]] = None) -> Optional[ExtractedTable]:
        lines = [line.strip() for line in table_str.strip().split("\n") if line.strip().startswith("|")]
        if len(lines) < 3:
            return None

        headers = [col.strip() for col in lines[0].strip("|").split("|")]
        rows = []
        for line in lines[2:]:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) == len(headers):
                rows.append(cells)

        id_match = re.search(r"Table\s+(\d+)", title)
        table_id = f"Table {id_match.group(1)}" if id_match else f"Table_{page_num}"

        return ExtractedTable(
            table_id=table_id,
            title=title,
            headers=headers,
            rows=rows,
            doc_id=doc_id,
            page_number=page_num,
            metadata_lines=meta_lines
        )

if __name__ == "__main__":
    parser = LayoutAwareParser()
    doc = parser.parse_document(Path("data/corpus/DOC-EHR-004.md"))
    print(f"Parsed {doc['doc_id']}: {len(doc['sections'])} sections, {len(doc['tables'])} tables.")

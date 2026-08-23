import os
import pdfplumber
from typing import List, Dict, Any
from app.config import DATA_DIR, SOURCE_PRECEDENCE

class DocumentChunk:
    def __init__(self, doc_id: str, title: str, content: str, file_name: str, 
                 status: str, precedence: int, account_id: str = None, section: str = ""):
        self.doc_id = doc_id
        self.title = title
        self.content = content
        self.file_name = file_name
        self.status = status  # "CURRENT", "DEPRECATED"
        self.precedence = precedence  # 1 = highest
        self.account_id = account_id  # If customer agreement, e.g. "ACCT-001"
        self.section = section

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "content": self.content,
            "file_name": self.file_name,
            "status": self.status,
            "precedence": self.precedence,
            "account_id": self.account_id,
            "section": self.section
        }

class DocumentLoader:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = str(DATA_DIR)
        self.data_dir = data_dir
        self.chunks: List[DocumentChunk] = []
        self.load_documents()

    def load_documents(self):
        """Loads and chunks all PDF documents from data_dir."""
        pdf_files = [f for f in os.listdir(self.data_dir) if f.endswith(".pdf")]
        
        for file_name in sorted(pdf_files):
            file_path = os.path.join(self.data_dir, file_name)
            
            # Determine metadata based on filename
            status = "CURRENT"
            precedence = SOURCE_PRECEDENCE.get("current_policy", 2)
            account_id = None
            title = file_name.replace(".pdf", "").replace("_", " ")

            if "DEPRECATED" in file_name:
                status = "DEPRECATED"
                precedence = SOURCE_PRECEDENCE["deprecated_policy"]
            elif "Northstar" in file_name:
                precedence = SOURCE_PRECEDENCE["enterprise_agreement"]
                account_id = "ACCT-001"
            elif "LumenWorks" in file_name:
                precedence = SOURCE_PRECEDENCE["enterprise_agreement"]
                account_id = "ACCT-002"
            elif "Cancellation" in file_name or "SOP" in file_name:
                precedence = SOURCE_PRECEDENCE["current_sop"]
            elif "Product" in file_name:
                precedence = SOURCE_PRECEDENCE["product_ops"]

            try:
                with pdfplumber.open(file_path) as pdf:
                    full_text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text() or ""
                        full_text += page_text + "\n"

                # Split text into logical sections/paragraphs
                raw_sections = full_text.split("\n\n")
                chunk_index = 1
                
                for sec in raw_sections:
                    sec_clean = sec.strip()
                    if not sec_clean:
                        continue

                    # Determine section title if present
                    first_line = sec_clean.split("\n")[0]
                    sec_title = first_line if len(first_line) < 60 else f"Section {chunk_index}"

                    chunk = DocumentChunk(
                        doc_id=f"{file_name}_c{chunk_index}",
                        title=title,
                        content=sec_clean,
                        file_name=file_name,
                        status=status,
                        precedence=precedence,
                        account_id=account_id,
                        section=sec_title
                    )
                    self.chunks.append(chunk)
                    chunk_index += 1

            except Exception as e:
                print(f"Error loading {file_name}: {e}")

    def get_all_chunks() -> List[DocumentChunk]:
        return self.chunks

# Global loader instance
doc_db = DocumentLoader()

import pypandoc
from pathlib import Path

import pypandoc

def write_docx_from_markdown(markdown_path: Path, docx_path: Path) -> bool:
    try:
        pypandoc.convert_file(str(markdown_path), 'docx', outputfile=str(docx_path))
    except Exception:
        return False
    return docx_path.exists()
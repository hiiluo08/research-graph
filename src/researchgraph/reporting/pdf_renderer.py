import pypandoc
from pathlib import Path

import pypandoc

def write_pdf_from_markdown(markdown_path: Path, pdf_path: Path) -> bool:
    try:
        pypandoc.convert_file(str(markdown_path), 'pdf', outputfile=str(pdf_path))
    except Exception:
        return False
    return pdf_path.exists()
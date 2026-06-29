from pathlib import Path
from typing import Any

from researchgraph.utils.json import write_json


class ArtifactStore:
    def __init__(self, base_dir: str | Path = 'artifacts') -> None:
        self.base_dir = Path(base_dir)

    def run_dir(self, run_id: str) -> Path:
        path = self.base_dir / run_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_text(self, run_id: str, filename: str, content: str) -> Path:
        path = self.run_dir(run_id) / filename
        path.write_text(content, encoding="utf-8")
        return path
    
    def write_json(self, run_id: str, filename: str, data: Any) -> Path:
        path = self.run_dir(run_id) / filename
        write_json(path, data)
        return path
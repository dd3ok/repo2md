from pydantic import BaseModel
from typing import List

class RepoRequest(BaseModel):
    repo_url: str

class ExportRequest(BaseModel):
    repo_name: str
    exts: List[str] = []
    dirs: List[str] = []

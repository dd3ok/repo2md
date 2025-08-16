from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from app.models import RepoRequest, ExportRequest
from app.services import analyze_repo, export_repo

app = FastAPI(title="Repo2MD API")


@app.post("/analyze")
def analyze(req: RepoRequest):
    repo_name, tree, exts, dirs, dirs_tree = analyze_repo(req.repo_url)
    if not repo_name:
        return JSONResponse(status_code=400, content={"error": "git clone 실패"})
    return {
        "repo_name": repo_name,
        "tree": tree,
        "extensions": exts,
        "dirs": dirs,
        "dirs_tree": dirs_tree
    }


@app.post("/export/file")
def export_file(req: ExportRequest):
    """
    선택된 조건으로 파일(.md) 다운로드
    """
    md_path = export_repo(req.repo_name, req.exts, req.dirs)
    if not md_path:
        return JSONResponse(status_code=404, content={"error": "repo not found or no files selected"})
    return FileResponse(md_path, media_type="text/markdown", filename=md_path)


@app.post("/export/json")
def export_json(req: ExportRequest):
    """
    선택된 조건으로 JSON 응답 반환
    """
    md_path = export_repo(req.repo_name, req.exts, req.dirs)
    if not md_path:
        return JSONResponse(status_code=404, content={"error": "repo not found or no files selected"})

    # 결과 파일 읽어서 JSON으로 반환
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    return {
        "repo_name": req.repo_name,
        "export_file": md_path,
        "content": content
    }

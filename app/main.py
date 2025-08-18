from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, JSONResponse
from app.models import RepoRequest, ExportRequest, DirectExportRequest
from app.services import analyze_repo, export_repo, direct_export

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
    선택된 조건으로 파일(.md) 다운로드 (파일 저장 없이)
    """
    # export_repo는 이제 파일 경로가 아닌 md 콘텐츠 문자열을 반환
    md_content = export_repo(req.repo_name, req.exts, req.dirs)
    
    if not md_content:
        return JSONResponse(status_code=404, content={"error": "repo not found or no files selected"})
    
    # 다운로드될 파일 이름 설정
    download_filename = f"{req.repo_name}_export.md"
    
    # Response 객체를 사용하여 메모리의 내용을 바로 전송
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={download_filename}"}
    )


@app.post("/export/json")
def export_json(req: ExportRequest):
    """
    선택된 조건으로 JSON 응답 반환 (파일 저장 및 읽기 없이)
    """
    # export_repo는 이제 파일 경로가 아닌 md 콘텐츠 문자열을 반환합니다.
    md_content = export_repo(req.repo_name, req.exts, req.dirs)
    
    if not md_content:
        return JSONResponse(status_code=404, content={"error": "repo not found or no files selected"})

    # 더 이상 파일을 열 필요 없이, 받은 콘텐츠를 바로 사용합니다.
    return {
        "repo_name": req.repo_name,
        "export_file": f"{req.repo_name}_export.md", # 파일 이름은 가상으로 생성
        "content": md_content
    }


@app.post("/direct-export/file")
def direct_export_file(req: DirectExportRequest):
    """
    Repo URL을 받아 분석 후 바로 MD 파일 다운로드
    """
    repo_name, md_content = direct_export(req.repo_url, req.exts, req.dirs)

    if not md_content or not repo_name:
        return JSONResponse(status_code=404, content={"error": "레포지토리를 처리할 수 없거나 선택된 파일이 없습니다."})

    download_filename = f"{repo_name}_export.md"
    
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={download_filename}"}
    )
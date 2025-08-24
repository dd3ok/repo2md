import tempfile
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from typing import Optional
from pathlib import Path
import io

from .models import AnalyzeRequest, AnalyzeResponse, ExportRequest, ExportTextResponse
from .services import clone_repo_to_session, analyze_repo_path, unpack_zip_to_session
from .utils import safe_filename, session_dir, clean_session, collect_files_for_export, render_markdown

app = FastAPI(title="repo2md")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def index():
    return FileResponse("static/index.html")

@app.get("/config")
def get_config(request: Request):
    base = f"{request.url.scheme}://{request.url.netloc}"
    return {"API_URL": base}

@app.websocket("/ws/{session_id}")
async def ws_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    print(f"🔌 WebSocket 연결: {session_id}")
    try:
        while True:
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
            elif msg == "disconnect":
                print(f"🧹 클라이언트 종료 요청: {session_id}")
                await websocket.close()
                break
    except WebSocketDisconnect:
        print(f"🔌 WebSocket 연결 해제: {session_id}")
    except Exception as e:
        print(f"❌ WebSocket 오류: {e}")
        try:
            await websocket.close()
        except:
            pass
    finally:
        # 연결이 어떤 이유로든 종료되면 세션 폴더 정리
        clean_session(session_id)
        print(f"✅ 세션 정리 완료: {session_id}")

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_repo(req: AnalyzeRequest, x_session_id: Optional[str] = Header(None)):
    if not x_session_id:
        raise HTTPException(status_code=400, detail="Missing X-Session-Id header")
    try:
        repo_path, repo_name = clone_repo_to_session(x_session_id, req.repo_url)
        data = analyze_repo_path(repo_path, repo_name)
        return data
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 업로드 스트리밍 저장 유틸
async def save_upload_file(upload: UploadFile, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as f:
        while True:
            chunk = await upload.read(1024 * 1024)  # 1MB
            if not chunk:
                break
            f.write(chunk)
    await upload.seek(0)

@app.post("/analyze_zip", response_model=AnalyzeResponse)
async def analyze_zip(file: UploadFile = File(...), x_session_id: Optional[str] = Header(None)):
    if not x_session_id:
        raise HTTPException(status_code=400, detail="Missing X-Session-Id header")

    # 1) 업로드 ZIP은 OS 임시 디렉터리에 저장(세션 폴더 바깥)
    temp_dir = Path(tempfile.gettempdir())
    upload_name = f"{x_session_id}.zip"  # 세션별 단일 파일명(재업로드 시 교체)
    upload_path = temp_dir / upload_name

    # 2) 저장 (스트리밍)
    try:
        await save_upload_file(file, upload_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {e}")

    # 3) 저장 확인
    if not upload_path.exists() or upload_path.stat().st_size == 0:
        raise HTTPException(status_code=500, detail="Uploaded ZIP not found after save")

    # 4) 압축 해제 및 분석
    try:
        # unpack_zip_to_session: 세션 폴더(.repos/{sessionId})를 비운 뒤 upload_path를 그 폴더로 해제
        repo_path, repo_name = unpack_zip_to_session(x_session_id, upload_path)
        data = analyze_repo_path(repo_path, repo_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze zip: {e}")
    finally:
        # 5) 업로드 ZIP 즉시 삭제(임시 디렉터리 청소)
        try:
            upload_path.unlink()
        except Exception:
            pass

    return data


@app.post("/export/text", response_model=ExportTextResponse)
def export_text(req: ExportRequest, x_session_id: Optional[str] = Header(None)):
    if not x_session_id:
        raise HTTPException(status_code=400, detail="Missing X-Session-Id header")

    base = session_dir(x_session_id)
    repo_dir = base / req.repo_name
    if not repo_dir.exists():
        candidates = [d for d in base.iterdir() if d.is_dir()]
        if not candidates:
            raise HTTPException(status_code=400, detail="Repository not found in session")
        repo_dir = max(candidates, key=lambda d: d.stat().st_mtime)

    files = collect_files_for_export(repo_dir, req.dirs, req.exts)
    md = render_markdown(req.repo_name, repo_dir, files)
    return {"content": md}

@app.post("/export/file")
def export_file(req: ExportRequest, x_session_id: Optional[str] = Header(None)):
    if not x_session_id:
        raise HTTPException(status_code=400, detail="Missing X-Session-Id header")

    base = session_dir(x_session_id)
    repo_dir = base / req.repo_name
    if not repo_dir.exists():
        candidates = [d for d in base.iterdir() if d.is_dir()]
        if not candidates:
            raise HTTPException(status_code=400, detail="Repository not found in session")
        repo_dir = max(candidates, key=lambda d: d.stat().st_mtime)

    files = collect_files_for_export(repo_dir, req.dirs, req.exts)
    md = render_markdown(req.repo_name, repo_dir, files)
    data = md.encode("utf-8")
    filename = f"{req.repo_name}_export.md"

    return StreamingResponse(
        io.BytesIO(data),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
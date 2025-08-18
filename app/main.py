from app.utils import cleanup_all_repos
cleanup_all_repos()

import os, time, asyncio
from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.models import RepoRequest, ExportRequest
from app.services import analyze_repo, export_repo
from app.utils import cleanup_session_dir, cleanup_all_repos

app = FastAPI(title="Repo2MD API")

connected_sessions: dict[str, dict] = {}
PING_TIMEOUT = 120

@app.get("/config")
def get_config():
    return {"API_URL": os.getenv("API_BASE_URL", "http://127.0.0.1:8000")}

@app.post("/analyze")
def analyze(req: RepoRequest, x_session_id: str = Header(...)):
    repo_name, tree, exts, dirs, dirs_tree = analyze_repo(req.repo_url, x_session_id)
    if not repo_name:
        raise HTTPException(status_code=400, detail="git clone 실패")
    if x_session_id in connected_sessions:
        connected_sessions[x_session_id]["repos"].add(repo_name)
    return {"repo_name": repo_name, "tree": tree, "extensions": exts, "dirs": dirs, "dirs_tree": dirs_tree}

@app.post("/export/file")
def export_file(req: ExportRequest, x_session_id: str = Header(...)):
    md_content = export_repo(req.repo_name, req.exts, req.dirs, x_session_id)
    if not md_content:
        raise HTTPException(status_code=404, detail="repo not found or no files selected")
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={req.repo_name}_export.md"}
    )

@app.post("/export/text")
def export_text(req: ExportRequest, x_session_id: str = Header(...)):
    md_content = export_repo(req.repo_name, req.exts, req.dirs, x_session_id)
    if not md_content:
        raise HTTPException(status_code=404, detail="repo not found or no files selected")
    return {"repo_name": req.repo_name, "export_file": f"{req.repo_name}_export.md", "content": md_content}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    connected_sessions[session_id] = {"repos": set(), "last_ping": time.time()}
    print(f"세션 {session_id} 연결됨")
    try:
        while True:
            msg = await websocket.receive_text()
            if msg == "ping":
                connected_sessions[session_id]["last_ping"] = time.time()
                await websocket.send_text("pong")
            elif msg == "disconnect":
                await cleanup_session(session_id)
                await websocket.close()
                break
    except WebSocketDisconnect:
        await cleanup_session(session_id)


async def cleanup_session(session_id: str):
    connected_sessions.pop(session_id, None)
    cleanup_session_dir(session_id)
    print(f"🗑 세션 {session_id} 만료 → repo 정리 완료")

@app.on_event("startup")
async def start_cleanup_task():
    # 서버가 새로 뜰 때 repos 폴더 전체 제거
    cleanup_all_repos()

    async def check_sessions():
        while True:
            now = time.time()
            expired = [
                sid for sid, info in list(connected_sessions.items())
                if now - info["last_ping"] > PING_TIMEOUT
            ]
            for sid in expired:
                await cleanup_session(sid)
            await asyncio.sleep(30)

    asyncio.create_task(check_sessions())


static_file_path = "static/index.html"
if os.path.exists(static_file_path):
    @app.get("/")
    async def serve_index():
        return FileResponse(static_file_path)
    app.mount("/static", StaticFiles(directory="static"), name="static")

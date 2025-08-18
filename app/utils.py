import stat
import os, subprocess, shutil
from pathlib import Path   # ✅ 꼭 필요

# 클론된 레포지토리 관리 기본 디렉토리
REPOS_DIR = "repos"
DEFAULT_EXCLUDE_DIRS = {'.git', 'node_modules', '__pycache__', '.vscode', '.idea'}

def get_session_repo_path(session_id: str, repo_name: str) -> str:
    return os.path.join(REPOS_DIR, session_id, repo_name)

def git_clone(repo_url: str, session_id: str):
    """세션 단위 repo clone"""
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = get_session_repo_path(session_id, repo_name)
    os.makedirs(os.path.dirname(repo_path), exist_ok=True)

    if os.path.exists(repo_path):
        print(f"✅ '{repo_path}' 이미 존재 → 재사용")
        return repo_name
    try:
        subprocess.run(["git", "clone", repo_url, repo_path],
                       check=True, capture_output=True, text=True)
        print(f"✅ 클론 완료: {repo_path}")
        return repo_name
    except subprocess.CalledProcessError as e:
        print(f"❌ git clone 실패: {e.stderr}")
        return None

def handle_remove_exception(exc: OSError, path: str, info):
    """Windows에서 액세스 거부 파일도 강제로 삭제"""
    try:
        # 접근 거부나 읽기 전용 파일이라면 권한 해제 후 재시도
        os.chmod(path, stat.S_IWRITE)
        os.remove(path)
        print(f"⚠️ 삭제 재시도 성공: {path}")
    except Exception as e:
        print(f"🚨 삭제 실패 무시: {path} ({e})")

def cleanup_session_dir(session_id: str):
    """세션 디렉토리 전체 정리 (폴더까지 완전히 삭제)"""
    path = os.path.join("repos", session_id)
    if os.path.isdir(path):
        print(f"🗑 세션 {session_id} 디렉토리 삭제 시도: {path}")
        try:
            shutil.rmtree(path, onexc=handle_remove_exception)
            print(f"✅ 세션 {session_id} 폴더 완전 삭제 완료")
        except Exception as e:
            print(f"🚨 세션 폴더 삭제 최종 실패: {e}")

def cleanup_all_repos():
    """repos 루트는 남기고 내부 모든 세션/데이터 디렉토리 삭제"""
    if os.path.isdir(REPOS_DIR):
        print(f"🗑 서버 시작/종료: '{REPOS_DIR}' 내부 데이터 전체 삭제")
        for entry in os.listdir(REPOS_DIR):
            full_path = os.path.join(REPOS_DIR, entry)
            try:
                if os.path.isfile(full_path) or os.path.islink(full_path):
                    os.remove(full_path)
                elif os.path.isdir(full_path):
                    shutil.rmtree(full_path, onexc=handle_remove_exception)
            except Exception as e:
                print(f"⚠️ '{full_path}' 삭제 실패: {e}")
    else:
        # repos 폴더가 아예 없으면 새로 만들어 둠
        os.makedirs(REPOS_DIR, exist_ok=True)
        print(f"📂 '{REPOS_DIR}' 디렉토리 새로 생성됨")

def generate_tree_and_extensions(repo_path: str):
    exts = set()
    tree_lines = []
    root_path = Path(repo_path)

    def add_line(path: Path, prefix="", is_last=True):
        if path.name in DEFAULT_EXCLUDE_DIRS:
            return
        connector = "└── " if is_last else "├── "
        if path.is_dir():
            tree_lines.append(f"{prefix}{connector}{path.name}/")
            new_prefix = prefix + ("    " if is_last else "│   ")
            items = sorted(
                [p for p in path.iterdir()
                 if p.name not in DEFAULT_EXCLUDE_DIRS],
                key=lambda x: (x.is_file(), x.name.lower())
            )
            for i, item in enumerate(items):
                add_line(item, new_prefix, i == len(items) - 1)
        else:
            ext = path.suffix.lower()
            if ext:
                exts.add(ext)
            tree_lines.append(f"{prefix}{connector}{path.name}")

    tree_lines.append(f"{root_path.name}/")
    items = sorted([p for p in root_path.iterdir()
                   if p.name not in DEFAULT_EXCLUDE_DIRS],
                   key=lambda x: (x.is_file(), x.name.lower()))
    for i, item in enumerate(items):
        add_line(item, "    ", i == len(items) - 1)

    return "\n".join(tree_lines), sorted(list(exts))

def collect_dirs_list(repo_path: str):
    dirs = []
    for dirpath, dirnames, _ in os.walk(repo_path):
        dirnames[:] = [d for d in dirnames if d not in DEFAULT_EXCLUDE_DIRS]
        for d in dirnames:
            rel = os.path.relpath(os.path.join(dirpath, d), repo_path).replace("\\", "/")
            if rel != '.' and rel not in dirs:
                dirs.append(rel)
    return sorted(dirs)

def build_dir_tree(path: Path, root_path: Path):
    if path.name in DEFAULT_EXCLUDE_DIRS:
        return None
    relative_path_str = os.path.relpath(path, root_path).replace("\\", "/")
    if relative_path_str == '.':
        relative_path_str = path.name
    if path.is_dir():
        children = [build_dir_tree(child, root_path) for child in sorted(
            path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))]
        children = [c for c in children if c]
        return {
            "name": path.name,
            "path": relative_path_str if path != root_path else '.',
            "type": "directory",
            "children": children
        }
    else:
        return {"name": path.name, "path": relative_path_str, "type": "file"}

def collect_dirs_tree(repo_path: str):
    root_path = Path(repo_path)
    return build_dir_tree(root_path, root_path)

def collect_selected_files(repo_path: str, selected_exts: set, selected_dirs: list):
    file_contents = {}
    root_path = Path(repo_path)
    for path in root_path.rglob('*'):
        if any(part in DEFAULT_EXCLUDE_DIRS for part in path.parts):
            continue
        if path.is_file():
            relative_path = path.relative_to(root_path)
            # 디렉토리 필터
            if selected_dirs and '.' not in selected_dirs:
                parent = str(relative_path.parent).replace('\\', '/')
                if not any(parent == sel or parent.startswith(sel + '/') for sel in selected_dirs):
                    continue
            # 확장자 필터
            if selected_exts and path.suffix.lower() not in selected_exts:
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    file_contents[str(relative_path).replace("\\", "/")] = f.read()
            except Exception:
                continue
    return file_contents

def generate_md_content(repo_name: str, tree_str: str, file_contents: dict) -> str:
    """선택된 파일들을 Markdown 문자열로 반환"""
    ext_to_lang = {
        ".py": "python", ".js": "javascript", ".ts": "typescript", ".tsx": "typescript",
        ".jsx": "javascript", ".java": "java", ".kt": "kotlin", ".go": "go", ".rs": "rust",
        ".php": "php", ".html": "html", ".htm": "html", ".css": "css", ".json": "json",
        ".yml": "yaml", ".yaml": "yaml", ".md": "markdown", ".sql": "sql", ".sh": "bash"
    }

    md_parts = []
    md_parts.append("아래 프로젝트 트리와 코드를 분석하고 세션 동안 기억해\n")
    md_parts.append("이후 모든 답변은 반드시 이 분석을 참조해\n\n")
    md_parts.append(f"# {repo_name}\n\n")
    md_parts.append("## 프로젝트 트리\n")
    md_parts.append("```\n")
    md_parts.append(tree_str)
    md_parts.append("\n```\n\n")
    md_parts.append("## 코드\n\n")

    for rel_path, content in sorted(file_contents.items()):
        ext = os.path.splitext(rel_path)[1].lower()
        lang = ext_to_lang.get(ext, "")
        md_parts.append(f"### `{rel_path}`\n")
        md_parts.append(f"```{lang}\n")
        md_parts.append(content)
        md_parts.append("\n```\n\n")

    return "".join(md_parts)
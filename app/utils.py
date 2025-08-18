import os, subprocess, shutil
from pathlib import Path

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

def cleanup_session_dir(session_id: str):
    """세션 디렉토리 전체 정리"""
    path = os.path.join(REPOS_DIR, session_id)
    if os.path.isdir(path):
        print(f"🗑 세션 {session_id} 디렉토리 삭제")
        shutil.rmtree(path, ignore_errors=True)

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
        return {"name": path.name, "path": relative_path_str if path != root_path else '.', 
                "type": "directory", "children": children}
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
            if selected_dirs and '.' not in selected_dirs:
                parent = str(relative_path.parent).replace('\\', '/')
                if not any(parent == sel or parent.startswith(sel + '/') for sel in selected_dirs):
                    continue
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
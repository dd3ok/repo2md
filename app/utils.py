import os
import subprocess
import shutil
from pathlib import Path

# 무시할 기본 디렉토리들
DEFAULT_EXCLUDE_DIRS = {'.git', 'node_modules', '__pycache__', '.vscode', '.idea'}


def git_clone(repo_url: str):
    """레포지토리 클론 (이미 있으면 재사용)"""
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    if os.path.exists(repo_name):
        print(f"✅ '{repo_name}' 디렉토리가 이미 존재하므로 재사용합니다.")
        return repo_name
    try:
        print(f"🔄 '{repo_url}' 레포지토리를 클론하는 중...")
        subprocess.run(["git", "clone", repo_url], check=True, capture_output=True, text=True)
        print(f"✅ 클론 완료: {repo_name}")
        return repo_name
    except subprocess.CalledProcessError as e:
        print(f"❌ git clone 실패: {e.stderr}")
        return None


def generate_tree_and_extensions(root_dir: str):
    """프로젝트 트리 문자열과 감지된 확장자 목록 반환"""
    exts = set()
    tree_lines = []
    root_path = Path(root_dir)

    def add_line(path: Path, prefix="", is_last=True):
        if path.name in DEFAULT_EXCLUDE_DIRS:
            return
        connector = "└── " if is_last else "├── "
        if path.is_dir():
            tree_lines.append(f"{prefix}{connector}{path.name}/")
            new_prefix = prefix + ("    " if is_last else "│   ")
            try:
                items = sorted(
                    [p for p in path.iterdir() if p.name not in DEFAULT_EXCLUDE_DIRS],
                    key=lambda x: (x.is_file(), x.name.lower())
                )
                for i, item in enumerate(items):
                    add_line(item, new_prefix, i == len(items) - 1)
            except PermissionError:
                tree_lines.append(f"{new_prefix}└── [접근 불가]")
        else:
            ext = path.suffix.lower()
            if ext:
                exts.add(ext)
            tree_lines.append(f"{prefix}{connector}{path.name}")

    # 루트부터 시작
    tree_lines.append(f"{root_path.name}/")
    items = sorted(
        [p for p in root_path.iterdir() if p.name not in DEFAULT_EXCLUDE_DIRS],
        key=lambda x: (x.is_file(), x.name.lower())
    )
    for i, item in enumerate(items):
        add_line(item, "    ", i == len(items) - 1)

    return "\n".join(tree_lines), sorted(list(exts))


# ✅ [추가됨] repo 내 모든 디렉토리를 평면 리스트로 수집
def collect_dirs_list(root_dir: str):
    """repo 내 모든 디렉토리를 평면 리스트로 반환"""
    dirs = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in DEFAULT_EXCLUDE_DIRS]
        for d in dirnames:
            rel = os.path.relpath(os.path.join(dirpath, d), root_dir)
            rel = rel.replace("\\", "/")
            if rel not in dirs:
                dirs.append(rel)
    return sorted(dirs)


# ✅ [추가됨] repo 디렉토리 트리를 JSON-like 구조로 수집
def build_dir_tree(path: Path):
    if path.is_dir() and path.name not in DEFAULT_EXCLUDE_DIRS:
        return {
            "name": path.name.replace("\\", "/"),
            "children": [
                build_dir_tree(child) for child in sorted(path.iterdir())
                if child.is_dir() and child.name not in DEFAULT_EXCLUDE_DIRS
            ]
        }
    return None


def collect_dirs_tree(root_dir: str):
    return build_dir_tree(Path(root_dir))


# 선택된 파일 수집
def collect_selected_files(root_dir: str, selected_exts: set, selected_dirs: list):
    """선택된 확장자와 폴더만 포함하여 파일 내용 수집"""
    file_contents = {}
    root_path = Path(root_dir)
    for path in root_path.rglob('*'):
        if any(part in DEFAULT_EXCLUDE_DIRS for part in path.parts):
            continue
        if path.is_file():
            relative_path = path.relative_to(root_path)

            # 디렉토리 필터링
            if selected_dirs:
                if str(relative_path.parent) != '.' and not any(
                    str(relative_path.parent).replace('\\', '/').startswith(sel.replace('\\', '/'))
                    for sel in selected_dirs
                ):
                    continue

            # 확장자 필터링
            ext = path.suffix.lower()
            if selected_exts and ext not in selected_exts:
                continue

            try:
                with open(path, "r", encoding="utf-8", errors='ignore') as f:
                    content = f.read()
                file_contents[str(relative_path).replace('\\', '/')] = content
            except Exception:
                continue
    return file_contents


def save_to_md(output_filename: str, repo_name: str, tree_str: str, file_contents: dict):
    """선택된 파일들을 Markdown으로 저장"""
    if not output_filename.endswith(".md"):
        output_filename += ".md"

    ext_to_lang = {
        ".py": "python", ".js": "javascript", ".ts": "typescript", ".tsx": "typescript",
        ".jsx": "javascript", ".java": "java", ".kt": "kotlin", ".go": "go", ".rs": "rust",
        ".php": "php", ".html": "html", ".htm": "html", ".css": "css", ".json": "json",
        ".yml": "yaml", ".yaml": "yaml", ".md": "markdown", ".sql": "sql", ".sh": "bash"
    }

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(f"# 📦 Repo2MD Export: {repo_name}\n\n")
        f.write("## 📂 프로젝트 트리\n")
        f.write("```\n")
        f.write(tree_str)
        f.write("\n```\n\n")
        f.write("## 📜 선택된 파일 코드\n\n")

        for rel_path, content in sorted(file_contents.items()):
            ext = os.path.splitext(rel_path)[1].lower()
            lang = ext_to_lang.get(ext, "")
            f.write(f"### `{rel_path}`\n")
            f.write(f"```{lang}\n")
            f.write(content)
            f.write("\n```\n\n")

    print(f"🎉 '{output_filename}' 파일이 생성되었습니다.")
    return output_filename


def cleanup_repo(repo_name: str):
    """클론된 레포 디렉토리 삭제"""
    if os.path.isdir(repo_name):
        print(f"🧹 '{repo_name}' 디렉토리를 정리합니다.")
        shutil.rmtree(repo_name, ignore_errors=True)
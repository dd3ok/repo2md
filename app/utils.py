import os
import subprocess
import shutil
from pathlib import Path

# 클론된 레포지토리를 관리할 기본 디렉토리
REPOS_DIR = "repos" 
# 무시할 기본 디렉토리들
DEFAULT_EXCLUDE_DIRS = {'.git', 'node_modules', '__pycache__', '.vscode', '.idea'}

def get_repo_path(repo_name: str) -> str:
    """레포지토리 이름을 받아 전체 경로를 반환"""
    return os.path.join(REPOS_DIR, repo_name)

def git_clone(repo_url: str):
    """레포지토리 클론 (이미 있으면 재사용)"""
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = get_repo_path(repo_name)

    # 상위 디렉토리 생성
    os.makedirs(REPOS_DIR, exist_ok=True)

    if os.path.exists(repo_path):
        print(f"✅ '{repo_path}' 디렉토리가 이미 존재하므로 재사용합니다.")
        return repo_name
    try:
        print(f"🔄 '{repo_url}' 레포지토리를 '{repo_path}'에 클론하는 중...")
        # 지정된 경로에 클론하도록 수정
        subprocess.run(["git", "clone", repo_url, repo_path], check=True, capture_output=True, text=True)
        print(f"✅ 클론 완료: {repo_path}")
        return repo_name
    except subprocess.CalledProcessError as e:
        print(f"❌ git clone 실패: {e.stderr}")
        return None


def generate_tree_and_extensions(repo_name: str):
    """프로젝트 트리 문자열과 감지된 확장자 목록 반환"""
    root_dir = get_repo_path(repo_name)
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

    # 루트부터 시작 (표시되는 이름은 repo_name, 실제 경로는 root_path)
    tree_lines.append(f"{root_path.name}/")
    items = sorted(
        [p for p in root_path.iterdir() if p.name not in DEFAULT_EXCLUDE_DIRS],
        key=lambda x: (x.is_file(), x.name.lower())
    )
    for i, item in enumerate(items):
        add_line(item, "    ", i == len(items) - 1)

    return "\n".join(tree_lines), sorted(list(exts))


def collect_dirs_list(repo_name: str):
    """repo 내 모든 디렉토리를 평면 리스트로 반환"""
    root_dir = get_repo_path(repo_name)
    dirs = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in DEFAULT_EXCLUDE_DIRS]
        for d in dirnames:
            rel = os.path.relpath(os.path.join(dirpath, d), root_dir)
            rel = rel.replace("\\", "/")
            if rel != '.' and rel not in dirs:
                dirs.append(rel)
    return sorted(dirs)


def build_dir_tree(path: Path, root_path: Path):
    if path.is_dir() and path.name not in DEFAULT_EXCLUDE_DIRS:
        # 상대 경로를 이름으로 사용
        name = os.path.relpath(path, root_path).replace("\\", "/")
        if name == '.': name = path.name
        
        children = [
            build_dir_tree(child, root_path) for child in sorted(path.iterdir())
            if child.is_dir() and child.name not in DEFAULT_EXCLUDE_DIRS
        ]
        # children이 None이 아닌 경우만 필터링
        children = [c for c in children if c]

        return {
            "name": path.name, # 순수 디렉토리 이름
            "path": name,     # 루트로부터의 상대 경로
            "children": children
        }
    return None

def collect_dirs_tree(repo_name: str):
    root_path = Path(get_repo_path(repo_name))
    return build_dir_tree(root_path, root_path)


def collect_selected_files(repo_name: str, selected_exts: set, selected_dirs: list):
    """선택된 확장자와 폴더만 포함하여 파일 내용 수집"""
    root_dir = get_repo_path(repo_name)
    file_contents = {}
    root_path = Path(root_dir)
    for path in root_path.rglob('*'):
        if any(part in DEFAULT_EXCLUDE_DIRS for part in path.parts):
            continue
        if path.is_file():
            relative_path = path.relative_to(root_path)
            relative_path_str = str(relative_path.parent).replace('\\', '/')

            # 디렉토리 필터링
            if selected_dirs:
                 # 루트 디렉토리('.')를 포함시키고, 선택된 디렉토리로 시작하는지 검사
                if not any(
                    relative_path_str == sel or relative_path_str.startswith(sel + '/')
                    for sel in selected_dirs
                ):
                    # 만약 selected_dirs에 루트(보통 빈 문자열이나 '.')가 있다면 모든 파일을 포함해야 함
                    # 이 로직은 사용자가 'src'를 선택하면 src 하위 모든 것을 포함하도록 개선됨
                    continue

            # 확장자 필터링
            if selected_exts and path.suffix.lower() not in selected_exts:
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

    content = generate_md_content(repo_name, tree_str, file_contents)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"'{output_filename}' 파일이 생성되었습니다.")
    return output_filename


def cleanup_repo(repo_name: str):
    """클론된 레포 디렉토리 삭제"""
    repo_path = get_repo_path(repo_name)
    if os.path.isdir(repo_path):
        print(f"'{repo_path}' 디렉토리를 정리합니다.")
        shutil.rmtree(repo_path, ignore_errors=True)

def generate_md_content(repo_name: str, tree_str: str, file_contents: dict) -> str:
    """선택된 파일들을 Markdown 문자열로 생성하여 반환"""
    ext_to_lang = {
        ".py": "python", ".js": "javascript", ".ts": "typescript", ".tsx": "typescript",
        ".jsx": "javascript", ".java": "java", ".kt": "kotlin", ".go": "go", ".rs": "rust",
        ".php": "php", ".html": "html", ".htm": "html", ".css": "css", ".json": "json",
        ".yml": "yaml", ".yaml": "yaml", ".md": "markdown", ".sql": "sql", ".sh": "bash"
    }

    md_parts = []
    md_parts.append("아래 프로젝트 트리와 코드를 분석하고 세션 동안 기억해")
    md_parts.append("이후 모든 답변은 반드시 이 분석을 참조해")
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
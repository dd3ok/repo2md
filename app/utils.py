import os
import re
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Set, Tuple

# 프로젝트 루트에 .repos 디렉토리를 생성하여 임시 파일들을 안전하게 관리
SAFE_ROOT = Path(os.getenv("REPO2MD_ROOT", ".repos")).resolve()

def ensure_safe_root() -> Path:
    """SAFE_ROOT 디렉토리가 존재하는지 확인하고 없으면 생성합니다."""
    SAFE_ROOT.mkdir(parents=True, exist_ok=True)
    return SAFE_ROOT

def session_dir_path(session_id: str) -> Path:
    root = ensure_safe_root()
    d = (root / session_id).resolve()
    if root not in d.parents and d != root:
        raise ValueError("Invalid session path")
    return d

def session_dir(session_id: str) -> Path:
    # 작업용: 필요 시 생성
    d = session_dir_path(session_id)
    d.mkdir(parents=True, exist_ok=True)
    return d

def clean_session(session_id: str) -> None:
    """세션 ID에 해당하는 작업 디렉토리를 완전히 삭제한다(재생성 안 함)."""
    try:
        d = session_dir_path(session_id)  # 생성하지 않음
        if d.exists():
            import stat
            def handle_remove_readonly(func, path, exc):
                try:
                    os.chmod(path, stat.S_IWRITE)
                except Exception:
                    pass
                func(path)
            shutil.rmtree(d, onerror=handle_remove_readonly)
            print(f"✅ 세션 {session_id} 정리 완료: {d}")
        else:
            print(f"⚠️ 세션 {session_id} 디렉토리 없음: {d}")
    except Exception as e:
        print(f"❌ 세션 {session_id} 정리 중 오류: {e}")

def guess_repo_name_from_git_url(url: str) -> str:
    """Git URL에서 저장소 이름을 추측합니다."""
    base = url.strip().rstrip("/").split("/")[-1]
    if base.endswith(".git"):
        base = base[:-4]
    return base or "repository"

def list_files_and_extensions(base_dir: Path) -> Tuple[Dict, List[str]]:
    """
    지정된 디렉토리의 파일 구조 트리와 사용된 확장자 목록을 반환합니다.
    (기존 코드의 중복 로직을 제거하여 리팩토링됨)
    """
    extensions: Set[str] = set()

    def walk(current: Path) -> Dict:
        """재귀적으로 디렉토리를 탐색하며 트리 노드를 생성합니다."""
        # .(점)으로 시작하는 파일/디렉토리(예: .git)는 무시
        entries = sorted([p for p in current.iterdir() if not p.name.startswith(".")], key=lambda p: (p.is_file(), p.name.lower()))
        
        children = []
        for p in entries:
            if p.is_dir():
                children.append(walk(p))
            else:
                ext = p.suffix
                if ext:
                    extensions.add(ext)
                children.append({
                    "name": p.name,
                    "path": str(p.relative_to(base_dir)).replace("\\", "/"),
                    "type": "file"
                })

        return {
            "name": current.name,
            "path": str(current.relative_to(base_dir)).replace("\\", "/") if current != base_dir else "",
            "type": "directory",
            "children": children
        }

    tree = walk(base_dir)
    # 확장자 목록을 정렬하여 반환
    return tree, sorted(list(extensions))


def unzip_to(dir_path: Path, zip_file_path: Path) -> Path:
    if not zip_file_path.exists():
        raise FileNotFoundError(f"ZIP not found: {zip_file_path}")
    if zip_file_path.stat().st_size == 0:
        raise FileNotFoundError(f"ZIP empty: {zip_file_path}")

    with zipfile.ZipFile(zip_file_path, 'r') as zf:
        zf.extractall(dir_path)

    entries = [p for p in dir_path.iterdir() if not p.name.startswith(("__MACOSX", "."))]
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return dir_path

def collect_files_for_export(base_dir: Path, selected_dirs: List[str], selected_exts: List[str]) -> List[Path]:
    """사용자가 선택한 디렉토리와 확장자에 맞는 파일 목록을 수집합니다."""
    files_to_export: List[Path] = []
    
    # 선택된 디렉토리 목록을 set으로 변환하여 검색 성능 향상
    selected_dirs_set = set(d.strip("/") for d in selected_dirs)

    def is_in_selected_dir(rel_path: str) -> bool:
        # 아무 디렉토리도 선택하지 않으면 전체를 의미
        if not selected_dirs_set:
            return True
        # 루트("")가 선택되었으면 전체를 의미
        if "" in selected_dirs_set:
            return True

        # 파일의 경로가 선택된 디렉토리 중 하나에 포함되는지 확인
        return any(rel_path == d or rel_path.startswith(d + "/") for d in selected_dirs_set)

    for p in base_dir.rglob("*"):
        if p.is_file():
            rel_path_str = str(p.relative_to(base_dir)).replace("\\", "/")
            
            if not is_in_selected_dir(rel_path_str):
                continue
                
            # 확장자 필터링 (선택된 확장자가 있을 경우에만)
            if selected_exts and p.suffix not in selected_exts:
                continue
            
            files_to_export.append(p)
            
    return sorted(files_to_export, key=lambda x: str(x).lower())

def render_markdown(repo_name: str, base_dir: Path, files: List[Path]) -> str:
    """수집된 파일 목록을 기반으로 최종 마크다운 문자열을 생성합니다."""
    lines: List[str] = [f"# {repo_name}", ""]
    
    lines.append("아래 프로젝트 트리와 코드를 분석하고 세션 동안 기억해\n")
    lines.append("이후 모든 답변은 반드시 이 분석을 참조해\n\n")

    # --- 프로젝트 트리 생성 ---
    lines.append("## Project Tree")
    lines.append("```")
    
    tree_lines_list: List[str] = []
    def build_tree_lines(root: Path, prefix: str = ""):
        # .(점)으로 시작하는 파일/디렉토리 무시
        entries = sorted([p for p in root.iterdir() if not p.name.startswith(".")], key=lambda p: (p.is_file(), p.name.lower()))
        for i, p in enumerate(entries):
            connector = "└── " if i == len(entries) - 1 else "├── "
            tree_lines_list.append(f"{prefix}{connector}{p.name}")
            if p.is_dir():
                new_prefix = prefix + ("    " if i == len(entries) - 1 else "│   ")
                build_tree_lines(p, new_prefix)
    
    tree_lines_list.append(f"{base_dir.name}/")
    build_tree_lines(base_dir, "    ")
    lines.extend(tree_lines_list)

    lines.append("```")
    lines.append("")

    # --- 파일 내용 추가 ---
    lines.append("## Files")
    for f in files:
        rel_path = str(f.relative_to(base_dir)).replace("\\", "/")
        lines.append(f"### `{rel_path}`") # 파일 경로를 인라인 코드로 표시
        
        # 파일 확장자에 따라 언어 태그 추가 (구문 강조 개선)
        lang = f.suffix.lstrip('.')
        lines.append(f"```{lang}")
        
        try:
            # 파일을 UTF-8로 읽되, 오류 발생 시 대체 문자로 처리
            content = f.read_text(encoding="utf-8", errors="replace")
            lines.append(content)
        except Exception:
            lines.append("<binary or unreadable file>") # 이진 파일 또는 읽기 오류 처리
            
        lines.append("```")
        lines.append("")
        
    return "\n".join(lines)

def safe_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^\w.\-]+", "_", name)
    return name or "upload.zip"


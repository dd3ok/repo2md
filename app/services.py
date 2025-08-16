import os
from app.utils import (
    git_clone,
    generate_tree_and_extensions,
    collect_dirs_list,
    collect_dirs_tree,
    collect_selected_files,
    save_to_md,
    cleanup_repo,
)

def analyze_repo(repo_url: str):
    """
    레포를 클론하고 트리 구조, 확장자 목록, 디렉토리 목록을 반환
    """
    repo_name = git_clone(repo_url)
    if not repo_name:
        return None, None, None, None, None

    # 트리 문자열 & 확장자
    tree_str, exts = generate_tree_and_extensions(repo_name)

    # 디렉토리 평면 리스트 & 트리 구조
    dirs = collect_dirs_list(repo_name)
    dirs_tree = collect_dirs_tree(repo_name)

    return repo_name, tree_str, exts, dirs, dirs_tree


def export_repo(repo_name: str, exts: list, dirs: list):
    """
    선택된 확장자/디렉토리에 해당하는 파일만 Markdown으로 변환
    """
    if not repo_name or not os.path.exists(repo_name):
        return None

    # 파일들 수집
    selected_files = collect_selected_files(repo_name, set(exts), dirs)

    if not selected_files:
        print("⚠️ 선택된 조건에 맞는 파일 없음")
        return None

    # 트리 문자열 생성 (문서 앞부분에 넣기 위함)
    tree_str, _ = generate_tree_and_extensions(repo_name)

    md_path = f"{repo_name}_export.md"
    return save_to_md(md_path, repo_name, tree_str, selected_files)

import os
from app.utils import (
    git_clone, get_session_repo_path,
    generate_tree_and_extensions, collect_dirs_list,
    collect_dirs_tree, collect_selected_files,
    generate_md_content
)

def analyze_repo(repo_url: str, session_id: str):
    """레포 클론하고 세션 repo_path의 정보 반환"""
    repo_name = git_clone(repo_url, session_id)
    if not repo_name:
        return None, None, None, None, None
    repo_path = get_session_repo_path(session_id, repo_name)
    tree, exts = generate_tree_and_extensions(repo_path)
    dirs = collect_dirs_list(repo_path)
    dirs_tree = collect_dirs_tree(repo_path)
    return repo_name, tree, exts, dirs, dirs_tree

def export_repo(repo_name: str, exts: list, dirs: list, session_id: str) -> str | None:
    repo_path = get_session_repo_path(session_id, repo_name)
    if not os.path.exists(repo_path):
        return None
    selected_files = collect_selected_files(repo_path, set(exts), dirs)
    if not selected_files: return None
    tree_str, _ = generate_tree_and_extensions(repo_path)
    return generate_md_content(repo_name, tree_str, selected_files)

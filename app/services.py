# app/services.py
import subprocess
import shutil
from pathlib import Path
from typing import Tuple
from .utils import (
    session_dir, clean_session, guess_repo_name_from_git_url,
    list_files_and_extensions, unzip_to
)

def clone_repo_to_session(session_id: str, repo_url: str) -> Tuple[Path, str]:
    """
    Clone git repo into a unique dir under session dir.
    Returns (repo_path, repo_name)
    """
    base = session_dir(session_id)
    repo_name = guess_repo_name_from_git_url(repo_url)
    target = base / repo_name

    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
    # shallow clone for speed
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(target)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        # cleanup
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)
        msg = e.stderr.strip() or e.stdout.strip() or "git clone failed"
        raise RuntimeError(msg)
    return target, repo_name

def analyze_repo_path(repo_path: Path, repo_name: str):
    tree, exts = list_files_and_extensions(repo_path)
    return {
        "repo_name": repo_name,
        "extensions": exts,
        "dirs_tree": tree
    }

def unpack_zip_to_session(session_id: str, uploaded_zip_path: Path) -> Tuple[Path, str]:
    """
    Unzip file into session and return (repo_path, repo_name)
    """
    base = session_dir(session_id)
    # clear previous content but keep session folder itself
    for item in base.iterdir():
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
        else:
            try:
                item.unlink()
            except Exception:
                pass

    repo_root = unzip_to(base, uploaded_zip_path)
    repo_name = repo_root.name
    return repo_root, repo_name

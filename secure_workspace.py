import os
import hashlib
import shutil
import json
import tempfile
from pathlib import Path

DEFAULT_EXCLUDE = [
    ".git", ".svn", ".hg", "__pycache__", ".pyc", ".pyo", ".pyd",
    ".pytest_cache", ".coverage", ".eggs", "node_modules",
    ".idea", ".vscode", ".vs", "*.swp", "*.swo",
    ".DS_Store", "Thumbs.db"
]

class SecureWorkspace:
    def __init__(self, home_dir=None, exclude_patterns=None):
        self.home = Path(home_dir or Path.home())
        self.exclude = exclude_patterns or DEFAULT_EXCLUDE
        self.snapshot = {}
        self.backup_dir = Path(tempfile.gettempdir()) / "secure_workspace_backup"
        self.snapshot_file = self.backup_dir / "snapshot.json"

    def is_excluded(self, path):
        return any(pattern in str(path) for pattern in self.exclude)

    def hash_file(self, file_path):
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def scan_directory(self):
        state = {}
        for root, _, files in os.walk(self.home):
            for name in files:
                full_path = Path(root) / name
                if self.is_excluded(full_path) or not full_path.is_file():
                    continue
                try:
                    rel_path = full_path.relative_to(self.home)
                    state[str(rel_path)] = self.hash_file(full_path)
                except Exception:
                    continue
        return state

    def save_snapshot(self):
        self.backup_dir.mkdir(exist_ok=True)
        self.snapshot = self.scan_directory()
        with open(self.snapshot_file, 'w') as f:
            json.dump(self.snapshot, f, indent=2)

    def load_snapshot(self):
        with open(self.snapshot_file, 'r') as f:
            self.snapshot = json.load(f)

    def backup_files(self):
        for rel_path in self.snapshot:
            src = self.home / rel_path
            dst = self.backup_dir / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.exists():
                shutil.copy2(src, dst)

    def detect_changes(self):
        current = self.scan_directory()
        added, modified, deleted = [], [], []

        for path, hash in current.items():
            if path not in self.snapshot:
                added.append(path)
            elif self.snapshot[path] != hash:
                modified.append(path)

        for path in self.snapshot:
            if path not in current:
                deleted.append(path)

        return added, modified, deleted

    def restore_file(self, rel_path):
        backup_file = self.backup_dir / rel_path
        target_file = self.home / rel_path
        if backup_file.exists():
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_file, target_file)

    def remove_file(self, rel_path):
        target_file = self.home / rel_path
        if target_file.exists():
            target_file.unlink()

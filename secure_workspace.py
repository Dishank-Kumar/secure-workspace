import os
import hashlib
import shutil
import json
import tempfile
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

DEFAULT_EXCLUDE = [
    ".git", ".svn", ".hg", "__pycache__", ".pyc", ".pyo", ".pyd",
    ".pytest_cache", ".coverage", ".eggs", "node_modules",
    ".idea", ".vscode", ".vs", "*.swp", "*.swo",
    ".DS_Store", "Thumbs.db", ".cache", ".tmp", "temp",
    ".mozilla", ".config", ".local/share", "snap", ".steam",
    ".wine", "AppData", "Library", ".Trash"
]

# Common directories to skip for performance
SKIP_DIRECTORIES = [
    ".git", ".svn", ".hg", "__pycache__", ".pytest_cache",
    "node_modules", ".cache", ".tmp", "temp", ".mozilla",
    ".config/google-chrome", ".config/chromium", ".steam",
    ".wine", "AppData", "Library", ".Trash", "Downloads/temp",
    ".local/share/Steam", ".local/share/Trash", "snap"
]

class SecureWorkspace:
    def __init__(self, home_dir=None, exclude_patterns=None, max_depth=3, max_workers=4):
        self.home = Path(home_dir or Path.home())
        self.exclude = exclude_patterns or DEFAULT_EXCLUDE
        self.max_depth = max_depth  # Limit directory depth
        self.max_workers = max_workers  # Parallel processing
        self.snapshot = {}
        self.backup_dir = Path(tempfile.gettempdir()) / "secure_workspace_backup"
        self.snapshot_file = self.backup_dir / "snapshot.json"
        self._file_count = 0
        self._processed_count = 0

    def is_excluded(self, path):
        path_str = str(path)
        return any(pattern in path_str for pattern in self.exclude)

    def should_skip_directory(self, dir_path):
        """Check if directory should be skipped entirely"""
        dir_name = dir_path.name
        return any(skip_dir in str(dir_path) for skip_dir in SKIP_DIRECTORIES)

    def hash_file(self, file_path):
        """Fast file hashing with error handling"""
        try:
            hasher = hashlib.md5()  # MD5 is faster than SHA256 for our use case
            with open(file_path, 'rb') as f:
                # Read in larger chunks for better performance
                while chunk := f.read(65536):  # 64KB chunks
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, IOError, PermissionError):
            return None

    def scan_directory_fast(self):
        """Fast directory scanning with parallelization and depth limiting"""
        state = {}
        files_to_process = []
        
        print(f"Scanning workspace (max depth: {self.max_depth})...")
        
        # First pass: collect files with depth limiting
        for root, dirs, files in os.walk(self.home):
            root_path = Path(root)
            
            # Calculate depth from home directory
            try:
                relative_path = root_path.relative_to(self.home)
                depth = len(relative_path.parts)
                if depth > self.max_depth:
                    dirs.clear()  # Don't descend deeper
                    continue
            except ValueError:
                continue
            
            # Skip excluded directories
            if self.should_skip_directory(root_path):
                dirs.clear()  # Don't descend into this directory
                continue
            
            # Filter out directories to skip from further traversal
            dirs[:] = [d for d in dirs if not self.should_skip_directory(root_path / d)]
            
            # Collect files to process
            for name in files:
                full_path = root_path / name
                if self.is_excluded(full_path) or not full_path.is_file():
                    continue
                
                # Skip very large files (>100MB) for performance
                try:
                    if full_path.stat().st_size > 100 * 1024 * 1024:
                        print(f"Skipping large file: {full_path}")
                        continue
                except (OSError, IOError):
                    continue
                
                try:
                    rel_path = full_path.relative_to(self.home)
                    files_to_process.append((str(rel_path), full_path))
                except ValueError:
                    continue
        
        self._file_count = len(files_to_process)
        print(f"Found {self._file_count} files to process...")
        
        if not files_to_process:
            return state
        
        # Second pass: hash files in parallel
        def process_file(file_info):
            rel_path, full_path = file_info
            file_hash = self.hash_file(full_path)
            self._processed_count += 1
            
            if self._processed_count % 100 == 0:
                print(f"Processed {self._processed_count}/{self._file_count} files...")
            
            return rel_path, file_hash
        
        # Use ThreadPoolExecutor for parallel file processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, file_info): file_info 
                            for file_info in files_to_process}
            
            for future in as_completed(future_to_file):
                try:
                    rel_path, file_hash = future.result()
                    if file_hash:  # Only store if hash was successful
                        state[rel_path] = file_hash
                except Exception as e:
                    # Silently skip problematic files
                    continue
        
        print(f"Scan complete! Processed {len(state)} files.")
        return state

    def scan_directory(self):
        """Use the fast scanning method"""
        return self.scan_directory_fast()

    def save_snapshot(self):
        """Save snapshot with progress indication"""
        self.backup_dir.mkdir(exist_ok=True)
        print("Creating workspace snapshot...")
        self.snapshot = self.scan_directory()
        
        print("Saving snapshot data...")
        with open(self.snapshot_file, 'w') as f:
            json.dump(self.snapshot, f, indent=2)
        print(f"Snapshot saved with {len(self.snapshot)} files.")

    def load_snapshot(self):
        """Load snapshot with error handling"""
        try:
            with open(self.snapshot_file, 'r') as f:
                self.snapshot = json.load(f)
            print(f"Loaded snapshot with {len(self.snapshot)} files.")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading snapshot: {e}")
            self.snapshot = {}

    def backup_files(self):
        """Backup files with progress indication"""
        if not self.snapshot:
            print("No files to backup.")
            return
        
        print(f"Backing up {len(self.snapshot)} files...")
        backed_up = 0
        
        for rel_path in self.snapshot:
            src = self.home / rel_path
            dst = self.backup_dir / rel_path
            
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.exists():
                    shutil.copy2(src, dst)
                    backed_up += 1
                    
                    if backed_up % 50 == 0:
                        print(f"Backed up {backed_up}/{len(self.snapshot)} files...")
            except (OSError, IOError, shutil.Error):
                continue  # Skip problematic files
        
        print(f"Backup complete! Backed up {backed_up} files.")

    def detect_changes(self):
        """Fast change detection with progress indication"""
        print("Detecting changes...")
        current = self.scan_directory()
        added, modified, deleted = [], [], []

        # Find added and modified files
        for path, hash_val in current.items():
            if path not in self.snapshot:
                added.append(path)
            elif self.snapshot[path] != hash_val:
                modified.append(path)

        # Find deleted files
        for path in self.snapshot:
            if path not in current:
                deleted.append(path)

        print(f"Changes detected - Added: {len(added)}, Modified: {len(modified)}, Deleted: {len(deleted)}")
        return added, modified, deleted

    def restore_file(self, rel_path):
        """Restore file with error handling"""
        backup_file = self.backup_dir / rel_path
        target_file = self.home / rel_path
        try:
            if backup_file.exists():
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_file, target_file)
                return True
        except (OSError, IOError, shutil.Error):
            pass
        return False

    def remove_file(self, rel_path):
        """Remove file with error handling"""
        target_file = self.home / rel_path
        try:
            if target_file.exists():
                target_file.unlink()
                return True
        except (OSError, IOError):
            pass
        return False

'''
Thread-safe CSV file operations with proper locking.
This module provides safe CSV read/write operations with file locking
to prevent corruption when multiple processes access the same file.
License:    GNU Affero General Public License - https://www.gnu.org/licenses/agpl-3.0.en.html
version:    26.01.20.5.09
'''

import csv
import platform
import time
from pathlib import Path
from typing import List, Dict, Optional, Set
from contextlib import contextmanager


class CSVManager:
    """Thread-safe CSV file manager with locking support"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.is_windows = platform.system() == 'Windows'

    @contextmanager
    def _lock_file(self, file_handle, shared=False):
        """Context manager for file locking (cross-platform) with retry"""
        max_retries = 5
        retry_delay = 0.2
        locked = False
        try:
            if self.is_windows:
                try:
                    import msvcrt
                    lock_mode = msvcrt.LK_NBLCK if not shared else msvcrt.LK_NBRLCK
                    for attempt in range(max_retries):
                        try:
                            msvcrt.locking(file_handle.fileno(), lock_mode, 1)
                            locked = True
                            break
                        except OSError:
                            if attempt < max_retries - 1:
                                time.sleep(retry_delay * (attempt + 1))
                except ImportError:
                    pass
            else:
                try:
                    import fcntl
                    lock_type = fcntl.LOCK_EX if not shared else fcntl.LOCK_SH
                    fcntl.flock(file_handle.fileno(), lock_type)
                    locked = True
                except ImportError:
                    pass

            yield file_handle

        finally:
            if locked:
                if self.is_windows:
                    try:
                        import msvcrt
                        msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
                    except (ImportError, OSError):
                        pass
                else:
                    try:
                        import fcntl
                        fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
                    except (ImportError, OSError):
                        pass

    def read_all_rows(self) -> List[List[str]]:
        """Read all rows from CSV with shared lock"""
        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, 'r', encoding='utf-8', newline='') as f:
                with self._lock_file(f, shared=True):
                    reader = csv.reader(f)
                    return list(reader)
        except Exception as e:
            print(f"[WARNING] Error reading CSV {self.file_path}: {e}")
            return []

    def get_column_as_set(self, column_index: int = 0, skip_header: bool = True) -> Set[str]:
        """Get specific column as set (useful for job IDs)"""
        rows = self.read_all_rows()
        if skip_header and len(rows) > 0:
            rows = rows[1:]  # Skip header

        return {row[column_index] for row in rows if len(row) > column_index}

    def append_row(self, row_data: Dict[str, str], fieldnames: List[str]) -> bool:
        """Append a single row to CSV with exclusive lock"""
        try:
            # Create file with header if doesn't exist
            if not self.file_path.exists():
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.file_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

            # Append row with lock
            with open(self.file_path, 'a', encoding='utf-8', newline='') as f:
                with self._lock_file(f, shared=False):
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerow(row_data)

            return True

        except Exception as e:
            print(f"[WARNING] Error writing to CSV {self.file_path}: {e}")
            return False

    def safe_read_dict_rows(self) -> List[Dict[str, str]]:
        """Read all rows as dictionaries"""
        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, 'r', encoding='utf-8', newline='') as f:
                with self._lock_file(f, shared=True):
                    reader = csv.DictReader(f)
                    return list(reader)
        except Exception as e:
            print(f"[WARNING] Error reading CSV dict rows: {e}")
            return []


class CachedCSVManager(CSVManager):
    """CSV Manager with caching layer for performance"""

    def __init__(self, file_path: str, cache_ttl_seconds: int = 300):
        super().__init__(file_path)
        self.cache_ttl = cache_ttl_seconds
        self._cache: Optional[Set[str]] = None
        self._cache_time: Optional[float] = None

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if self._cache is None or self._cache_time is None:
            return False
        return (time.time() - self._cache_time) < self.cache_ttl

    def get_column_as_set_cached(self, column_index: int = 0, skip_header: bool = True) -> Set[str]:
        """Get column as set with caching"""
        if self._is_cache_valid():
            return self._cache

        # Refresh cache
        self._cache = self.get_column_as_set(column_index, skip_header)
        self._cache_time = time.time()
        return self._cache

    def invalidate_cache(self):
        """Manually invalidate cache (call after writes)"""
        self._cache = None
        self._cache_time = None

    def append_row(self, row_data: Dict[str, str], fieldnames: List[str]) -> bool:
        """Append row and invalidate cache"""
        success = super().append_row(row_data, fieldnames)
        if success:
            self.invalidate_cache()
        return success


############################################################################################################

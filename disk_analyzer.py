# Refactored disk_analyzer.py
#!/usr/bin/env python3

import time
import logging
from pathlib import Path
from typing import List, Generator
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
    path: str
    size: int
    is_dir: bool
    depth: int
    mtime: float

class DiskAnalyzer:
    def __init__(self, max_depth=8, max_files=100000, timeout_seconds=300, follow_symlinks=False, data_streamer=None):
        self.max_depth = max_depth
        self.max_files = max_files
        self.timeout_seconds = timeout_seconds
        self.follow_symlinks = False
        self.data_streamer = data_streamer
        self.start_time = time.time()
        self.visited_inodes = set()
        self.files = []

    def scan_directory(self, root_path: str) -> List[FileInfo]:
        root = Path(root_path).resolve()
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Invalid directory: {root_path}")

        logger.info(f"Starting scan: {root}")
        for file_info in self._walk(root, 0):
            self.files.append(file_info)
        return self.files

    def _walk(self, path: Path, depth: int) -> Generator[FileInfo, None, None]:
        if depth > self.max_depth:
            return

        try:
            entries = list(path.iterdir())
        except (PermissionError, OSError):
            return

        for entry in entries:
            if time.time() - self.start_time > self.timeout_seconds:
                logger.warning("Scan timeout")
                return
            if len(self.files) >= self.max_files:
                logger.warning("File limit reached")
                return
            try:
                stat_info = entry.lstat()
                if not self.follow_symlinks and entry.is_symlink():
                    continue
                inode_key = (stat_info.st_dev, stat_info.st_ino)
                if inode_key in self.visited_inodes:
                    continue
                self.visited_inodes.add(inode_key)
                size = stat_info.st_size
                if size == 0 and not entry.is_dir():
                    continue

                # --- ADD THIS ---
                logger.info(f"Found file: {entry} (size: {size} bytes, dir: {entry.is_dir()})")

                file_info = FileInfo(
                    path=str(entry),
                    size=size,
                    is_dir=entry.is_dir(),
                    depth=depth + 1,
                    mtime=stat_info.st_mtime
                )
                if self.data_streamer:
                    logger.info(f"Streaming file to callback: {file_info.path}")
                    self.data_streamer.add_file(file_info)
                yield file_info
                if entry.is_dir():
                    yield from self._walk(entry, depth + 1)
            except (PermissionError, OSError):
                continue


class RealTimeDataStreamer:
    def __init__(self, callback_function, update_interval=0.5):
        self.callback = callback_function
        self.interval = update_interval
        self.last_update = time.time()
        self.accumulated = []

    def add_file(self, file_info: FileInfo):
        self.accumulated.append(file_info)
        logger.info(f"RealTimeDataStreamer: added file {file_info.path}, accumulated count={len(self.accumulated)}")
        now = time.time()
        if now - self.last_update >= self.interval:
            self.flush()

    def flush(self):
        if not self.accumulated:
            logger.info("RealTimeDataStreamer.flush() called but no files to flush")
            return
        logger.info(f"RealTimeDataStreamer.flush() called, flushing {len(self.accumulated)} files to callback")
        try:
            self.callback(self.accumulated)
        except Exception as e:
            logger.error(f"Streamer error during flush: {e}")
        self.accumulated.clear()
        self.last_update = time.time()

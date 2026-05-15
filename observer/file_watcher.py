import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from observer.activity_logger import init_db, log_event

IGNORED_DIRS = {'.git', '.venv', '__pycache__', 'node_modules', '.idea'}
IGNORED_EXTS = {'.pyc', '.pyo', '.db', '.log'}

class GruntKillHandler(FileSystemEventHandler):

    def should_ignore(self, path):
        parts = path.replace("\\", "/").split("/")
        for part in parts:
            if part in IGNORED_DIRS:
                return True
        _, ext = os.path.splitext(path)
        if ext in IGNORED_EXTS:
            return True
        return False

    def on_created(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            log_event("file_created", event.src_path, os.getcwd())
            print(f"[+] Created: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            log_event("file_modified", event.src_path, os.getcwd())
            print(f"[~] Modified: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            log_event("file_deleted", event.src_path, os.getcwd())
            print(f"[-] Deleted: {event.src_path}")

    def on_moved(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            data = f"{event.src_path} -> {event.dest_path}"
            log_event("file_moved", data, os.getcwd())
            print(f"[>] Moved: {data}")

def start_watcher(watch_path="."):
    init_db()
    observer = Observer()
    handler = GruntKillHandler()
    observer.schedule(handler, path=watch_path, recursive=True)
    observer.start()
    print(f"✓ File watcher running on: {os.path.abspath(watch_path)}")
    print("  Press Ctrl+C to stop\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n✓ File watcher stopped")
    observer.join()

if __name__ == "__main__":
    start_watcher(".")
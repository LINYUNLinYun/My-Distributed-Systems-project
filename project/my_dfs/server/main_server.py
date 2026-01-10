import os
import time
import threading
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn

STORAGE_DIR = "storage_server"
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class FileServer:
    def __init__(self):
        self.locks = {}
        self.mutex = threading.Lock()
        print(f"Server running. Root: {os.path.abspath(STORAGE_DIR)}")

    def _get_path(self, filename):
        return os.path.join(STORAGE_DIR, filename)

    def list_files(self):
        return os.listdir(STORAGE_DIR)

    def get_file_info(self, filename):
        filepath = self._get_path(filename)
        if os.path.exists(filepath):
            return {"exists": True, "mtime": os.path.getmtime(filepath)}
        return {"exists": False, "mtime": 0}

    def read_file(self, filename):
        filepath = self._get_path(filename)
        if os.path.exists(filepath):
            # === 故意增加2秒延迟，用于演示缓存效果 ===
            print(f"Server: Reading {filename} from disk (Simulating 2s latency)...")
            time.sleep(2) 
            # ========================================
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def create_file(self, filename):
        filepath = self._get_path(filename)
        if os.path.exists(filepath): return False
        with open(filepath, 'w', encoding='utf-8') as f: f.write("")
        return True

    def write_file(self, filename, content, client_id):
        with self.mutex:
            if filename in self.locks and self.locks[filename] != client_id:
                raise Exception("Server: Locked by another user.")
        filepath = self._get_path(filename)
        with open(filepath, 'w', encoding='utf-8') as f: f.write(content)
        return True

    def delete_file(self, filename, client_id):
        with self.mutex:
             if filename in self.locks and self.locks[filename] != client_id:
                raise Exception("Server: Locked by another user.")
        filepath = self._get_path(filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    def acquire_lock(self, filename, client_id):
        with self.mutex:
            if filename not in self.locks:
                self.locks[filename] = client_id
                print(f"Lock: {filename} -> {client_id}")
                return True
            return self.locks[filename] == client_id

    def release_lock(self, filename, client_id):
        with self.mutex:
            if filename in self.locks and self.locks[filename] == client_id:
                del self.locks[filename]
                print(f"Unlock: {filename} -> {client_id}")
                return True
            return False

if __name__ == "__main__":
    # 将 'localhost' 改为 '127.0.0.1'
    server = ThreadedXMLRPCServer(('127.0.0.1', 8000), allow_none=True)
    server.register_instance(FileServer())
    print("Serving on 127.0.0.1 port 8000...")
    server.serve_forever()
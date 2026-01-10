import xmlrpc.client
import uuid
import time
import os

class DFSClient:
    def __init__(self, server_url='http://127.0.0.1:8000'):
        self.server = xmlrpc.client.ServerProxy(server_url)
        self.client_id = str(uuid.uuid4()) # 生成唯一的客户端ID
        # 内存缓存: {filename: {'content': str, 'mtime': float}}
        self.cache = {} 
        print(f"Client initialized with ID: {self.client_id}")

    def list_files(self):
        return self.server.list_files()

    def create(self, filename):
        return self.server.create_file(filename)

    def read(self, filename):
        """带有缓存机制的读取"""
        # 1. 获取服务器端文件的元数据
        server_info = self.server.get_file_info(filename)
        
        if not server_info['exists']:
            print(f"File {filename} does not exist on server.")
            return None

        # 2. 检查本地缓存是否有效
        if filename in self.cache:
            local_mtime = self.cache[filename]['mtime']
            if local_mtime == server_info['mtime']:
                print(f"[CACHE HIT] Reading {filename} from local cache.")
                return self.cache[filename]['content']
        
        # 3. 缓存失效或不存在，从服务器拉取
        print(f"[CACHE MISS] Fetching {filename} from server...")
        content = self.server.read_file(filename)
        
        # 4. 更新本地缓存
        if content is not None:
            self.cache[filename] = {
                'content': content,
                'mtime': server_info['mtime']
            }
        return content

    def write(self, filename, content):
        """写入流程：获取锁 -> 写入 -> 更新缓存 -> 释放锁"""
        print(f"Attempting to write to {filename}...")
        
        # 1. 获取锁
        if not self.server.acquire_lock(filename, self.client_id):
            print(f"Failed to acquire lock for {filename}. Another user is editing.")
            return False
        
        try:
            # 2. 写入服务器
            self.server.write_file(filename, content, self.client_id)
            
            # 3. 既然我刚写完，我也应该更新我自己的缓存
            # 注意：实际分布式系统中可能需要重新获取mtime，这里简化处理
            self.cache[filename] = {
                'content': content,
                'mtime': time.time() # 近似时间，或者再次调用 get_file_info
            }
            print(f"Write successful to {filename}.")
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False
        finally:
            # 4. 释放锁
            self.server.release_lock(filename, self.client_id)

    def delete(self, filename):
        if not self.server.acquire_lock(filename, self.client_id):
            print("Could not acquire lock to delete file.")
            return False
        try:
            res = self.server.delete_file(filename, self.client_id)
            if res:
                # 同时也删除本地缓存
                if filename in self.cache:
                    del self.cache[filename]
                print(f"File {filename} deleted.")
            return res
        finally:
            self.server.release_lock(filename, self.client_id)
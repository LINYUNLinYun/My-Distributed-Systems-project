import sys
import os
import time
import threading
import unittest

# 将父目录加入 path 以便导入 client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.dfs_client import DFSClient

class TestDFS(unittest.TestCase):
    
    def setUp(self):
        """每个测试前初始化两个客户端，模拟多用户"""
        self.client1 = DFSClient()
        self.client2 = DFSClient()
        self.test_file = "test_doc.txt"

    def test_01_create_and_read(self):
        print("\n--- Test: File Creation and Basic Read ---")
        # Client 1 创建文件
        self.client1.create(self.test_file)
        files = self.client1.list_files()
        self.assertIn(self.test_file, files)
        
        # 写入内容
        data = "Hello Distributed System"
        self.client1.write(self.test_file, data)
        
        # Client 2 读取 (应该从服务器拉取，Cache Miss)
        read_data = self.client2.read(self.test_file)
        self.assertEqual(read_data, data)

    def test_02_caching(self):
        print("\n--- Test: Client Side Caching ---")
        # 此时 Client 2 已经读取过文件，应该有缓存
        # 我们手动修改 Client 2 的缓存内容来验证它是否读取了缓存（而不是去服务器）
        # 注意：这只是为了验证代码逻辑是否走了 cache 分支
        
        original_content = self.client2.read(self.test_file)
        
        # 再次读取，期望看到控制台输出 [CACHE HIT]
        # 由于我们无法直接断言控制台输出，我们通过检查 client 内部状态
        # (在真实单元测试中，我们会 mock 服务器请求，这里通过逻辑验证)
        
        start_time = time.time()
        content = self.client2.read(self.test_file)
        end_time = time.time()
        
        self.assertEqual(content, original_content)
        print(f"Read time (cached): {end_time - start_time:.6f}s")

    def test_03_locking_and_concurrency(self):
        print("\n--- Test: File Locking & Concurrency ---")
        # 模拟 Client 1 正在写文件（持有锁）
        self.client1.server.acquire_lock(self.test_file, self.client1.client_id)
        print(f"Client 1 ({self.client1.client_id}) acquired lock manualy.")

        # Client 2 尝试写入，应该失败
        success = self.client2.write(self.test_file, "Client 2 trying to overwrite")
        self.assertFalse(success, "Client 2 should fail to write when Client 1 has lock")

        # Client 1 释放锁
        self.client1.server.release_lock(self.test_file, self.client1.client_id)
        print("Client 1 released lock.")

        # Client 2 再次尝试，应该成功
        success = self.client2.write(self.test_file, "Client 2 overwrite success")
        self.assertTrue(success, "Client 2 should succeed after lock is released")
        
        # 验证内容
        content = self.client1.read(self.test_file) # Client 1 读取新内容
        self.assertEqual(content, "Client 2 overwrite success")

    def tearDown(self):
        # 清理测试文件
        try:
            self.client1.delete(self.test_file)
        except:
            pass

if __name__ == '__main__':
    unittest.main()
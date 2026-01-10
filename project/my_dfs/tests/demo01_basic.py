import sys
import os
# 添加路径以便导入 client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client.dfs_client import DFSClient

def run():
    print("=== 演示 1: 基本文件操作 (增删改查) ===")
    client = DFSClient()
    filename = "demo_basic.txt"

    # 1. Create
    print(f"\n[1] 创建文件 '{filename}'...")
    if client.create(filename):
        print(" -> 成功.")
    else:
        print(" -> 文件已存在.")

    # 2. Write
    content = "Hello Distributed System!"
    print(f"\n[2] 写入内容: '{content}'...")
    client.write(filename, content)

    # 3. Read
    print(f"\n[3] 读取文件...")
    data = client.read(filename)
    print(f" -> 读取结果: {data}")
    assert data == content

    # 4. List
    print(f"\n[4] 文件列表: {client.list_files()}")

    # 5. Delete
    print(f"\n[5] 删除文件...")
    client.delete(filename)
    print(" -> 删除完成.")
    
    print("\n[演示完成]")

if __name__ == "__main__":
    run()
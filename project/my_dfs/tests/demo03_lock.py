import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client.dfs_client import DFSClient

def run():
    print("=== 演示 3: 多用户并发与文件锁 ===")
    filename = "demo_lock.txt"
    
    # 模拟两个用户
    user_A = DFSClient()  # User A
    user_B = DFSClient()  # User B
    print(f"User A ID: {user_A.client_id}")
    print(f"User B ID: {user_B.client_id}\n")

    # 初始化
    user_A.create(filename)
    user_A.write(filename, "Initial Content")

    # 1. User A 加锁
    print(f"[1] User A 对 '{filename}' 手动加锁...")
    user_A.server.acquire_lock(filename, user_A.client_id)
    print(" -> User A 锁定了文件。")

    # 2. User B 尝试写入 (应该失败)
    print(f"\n[2] User B 尝试写入文件...")
    success = user_B.write(filename, "User B trying to hack in")
    if not success:
        print("✔ 预期结果：User B 写入失败 (被锁拒绝)。")
    else:
        print("❌ 错误：User B 竟然写入成功了！锁机制失效。")

    # 3. User A 解锁
    print(f"\n[3] User A 释放锁...")
    user_A.server.release_lock(filename, user_A.client_id)
    print(" -> 锁已释放。")

    # 4. User B 再次尝试写入 (应该成功)
    print(f"\n[4] User B 再次尝试写入...")
    success = user_B.write(filename, "User B content")
    if success:
        print("✔ 预期结果：User B 写入成功。")
        # 验证内容
        print(f" -> 最终文件内容: {user_A.read(filename)}")
    else:
        print("❌ 错误：User B 依然无法写入。")

    # 清理
    user_A.delete(filename)

if __name__ == "__main__":
    run()
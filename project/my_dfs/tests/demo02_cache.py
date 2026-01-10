import sys
import os
import time
# 确保能导入 client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client.dfs_client import DFSClient

def run():
    print("===============================================")
    print("      演示 2: 客户端缓存机制完整测试")
    print("      (包含：缓存命中加速 + 缓存一致性更新)")
    print("===============================================\n")
    
    # 模拟两个客户端
    client_A = DFSClient()  # 用户 A (主要观察者)
    client_B = DFSClient()  # 用户 B (捣乱者/修改者)
    
    filename = "cache_test_combined.txt"
    
    # --- 初始化 ---
    print(">>> [初始化] 创建文件 V1 版本...")
    client_A.create(filename)
    client_A.write(filename, "Version 1: Hello World")
    
    # ==========================================
    # 第一部分：验证缓存命中 (Cache Hit)
    # ==========================================
    print("\n-------------------------------------------")
    print("PART 1: 验证缓存加速 (Cache Speed)")
    print("-------------------------------------------")

    # 1. 第一次读取 (冷启动)
    print("1. 用户 A 第一次读取 (Cache MISS)...")
    print("   (预期: 服务器强制延迟 2s，速度较慢)")
    start = time.time()
    data1 = client_A.read(filename)
    t1 = time.time() - start
    print(f"   -> 内容: {data1}")
    print(f"   -> 耗时: {t1:.4f} 秒")

    # 2. 第二次读取 (热缓存)
    print("\n2. 用户 A 第二次读取 (Cache HIT)...")
    print("   (预期: 直接读内存，速度极快 ≈0s)")
    start = time.time()
    data2 = client_A.read(filename)
    t2 = time.time() - start
    print(f"   -> 内容: {data2}")
    print(f"   -> 耗时: {t2:.4f} 秒")

    if t2 < 0.1 and t1 > 1.5:
        print("\n✔ [通过]: 缓存加速生效。")
    else:
        print("\n❌ [失败]: 速度差异不明显，请检查服务端配置。")

    # ==========================================
    # 第二部分：验证缓存一致性 (Cache Consistency)
    # ==========================================
    print("\n-------------------------------------------")
    print("PART 2: 验证缓存一致性 (Consistency)")
    print("-------------------------------------------")
    
    # 为了确保文件系统的时间戳(mtime)发生变化，这里稍微等待一下
    # (某些系统 mtime 精度为1秒)
    print("3. 等待 1.5秒 以确保时间戳变化...")
    time.sleep(1.5)

    # 3. 用户 B 修改文件
    print("\n4. 用户 B 在后台修改文件为 V2 版本...")
    client_B.write(filename, "Version 2: Python Distributed System")
    print("   -> 服务器端文件已更新。")

    # 4. 用户 A 第三次读取
    print("\n5. 用户 A 第三次读取...")
    print("   (预期: 检测到服务器变动 -> 重新下载 -> 耗时变回 >2s)")
    
    start = time.time()
    data3 = client_A.read(filename) # 内部逻辑应触发 mtime 对比失败，从而重新下载
    t3 = time.time() - start
    
    print(f"   -> 内容: {data3}")
    print(f"   -> 耗时: {t3:.4f} 秒")

    # --- 最终判定 ---
    print("\n-------------------------------------------")
    print("              测试总结")
    print("-------------------------------------------")
    
    is_content_new = "Version 2" in data3
    is_slow_again = t3 > 1.5

    if is_content_new and is_slow_again:
        print("✔ [完美]:")
        print("  1. 本地缓存生效 (变快了)。")
        print("  2. 远程更新被检测到 (自动刷新了)。")
        print("  符合题目要求：(4) 本地存储搜索 + 一致性支持。")
    elif not is_content_new:
        print("❌ [严重失败]: 读到了旧缓存！一致性未保证。")
    elif not is_slow_again:
        print("❓ [疑问]: 读到了新内容，但速度太快？可能是 mtime 检查耗时忽略不计。")

    # 清理
    try:
        client_A.delete(filename)
    except:
        pass

if __name__ == "__main__":
    run()
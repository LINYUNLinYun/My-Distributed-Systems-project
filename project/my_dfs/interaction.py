import sys
import os
from client.dfs_client import DFSClient

def print_help():
    print("\n=== 分布式文件系统交互终端 ===")
    print("支持命令:")
    print("  ls            - 列出所有文件")
    print("  create <name> - 创建新文件")
    print("  read <name>   - 读取文件内容")
    print("  write <name> <content> - 写入内容到文件")
    print("  rm <name>     - 删除文件")
    print("  exit          - 退出")
    print("==============================\n")

def main():
    try:
        client = DFSClient()
        print(f"已连接到 DFS Server. 客户端 ID: {client.client_id}")
    except Exception as e:
        print("连接服务器失败，请确保 run_test.bat 中的 server 正在运行。")
        return

    print_help()

    while True:
        try:
            command = input("DFS> ").strip().split()
            if not command:
                continue

            cmd = command[0].lower()

            if cmd == 'exit':
                break
            
            elif cmd == 'ls':
                files = client.list_files()
                print(f"Files: {files}")

            elif cmd == 'create':
                if len(command) < 2:
                    print("Usage: create <filename>")
                    continue
                if client.create(command[1]):
                    print(f"Success: File '{command[1]}' created.")
                else:
                    print(f"Error: File '{command[1]}' already exists or failed.")

            elif cmd == 'read':
                if len(command) < 2:
                    print("Usage: read <filename>")
                    continue
                content = client.read(command[1])
                if content is not None:
                    print(f"--- Content of {command[1]} ---")
                    print(content)
                    print("-----------------------------")
                else:
                    print("Error: File not found.")

            elif cmd == 'write':
                if len(command) < 3:
                    print("Usage: write <filename> <content_string>")
                    continue
                filename = command[1]
                content = " ".join(command[2:]) # 允许内容包含空格
                if client.write(filename, content):
                    print(f"Success: Written to '{filename}'.")
                else:
                    print("Error: Write failed (Lock issue?).")

            elif cmd == 'rm':
                if len(command) < 2:
                    print("Usage: rm <filename>")
                    continue
                if client.delete(command[1]):
                    print(f"Success: File '{command[1]}' deleted.")
                else:
                    print("Error: Delete failed.")
            else:
                print("Unknown command.")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"System Error: {e}")

if __name__ == "__main__":
    main()
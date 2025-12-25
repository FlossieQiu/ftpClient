import os
import threading
import sys
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# 全局变量，用于在主线程控制服务器关闭
server = None

def start_ftp_server():
    global server
    
    # 1. 创建测试目录
    test_root = "ftp_test_root"

    if not os.path.exists(test_root):
        os.makedirs(test_root)
    # 创建子目录
    empty_dir = os.path.join(test_root, "empty_dir")  # 构建子目录路径
    if not os.path.exists(empty_dir):
        os.makedirs(empty_dir)

    # 2. 配置权限
    authorizer = DummyAuthorizer()
    # user=test, password=test123, perm=elradfmwMT (读写删全权限)
    authorizer.add_user("test", "test123", test_root, perm="elradfmwMT")
    # 匿名用户
    authorizer.add_anonymous(test_root, perm="elradfmwMT")

    # 3. 配置 Handler
    handler = FTPHandler
    handler.authorizer = authorizer
    # 显式指定编码为 UTF-8
    handler.encoding = 'utf-8'

    # 4. 初始化服务器
    address = ("127.0.0.1", 2121)
    server = FTPServer(address, handler)

    # 减少日志干扰 (可选)
    # import logging
    # logging.basicConfig(level=logging.ERROR) 

    print(f"\n==========================================")
    print(f"FTP Server Started at ftp://127.0.0.1:2121")
    print(f"Root directory: {os.path.abspath(test_root)}")
    print(f"User: test / test123")
    print(f"==========================================")
    
    # 5. 启动服务 (这是一个阻塞调用，会在这个线程中一直运行)
    server.serve_forever()

def main():
    # 创建一个线程来运行 FTP 服务器
    t = threading.Thread(target=start_ftp_server)
    t.daemon = True # 设置为守护线程，主程序退出时它也会退出
    t.start()

    # 主线程循环监听键盘输入
    print("\n>>> 服务器正在运行中。按 'q' 然后回车 (Enter) 以停止服务器...\n")
    
    while True:
        try:
            user_input = input()
            if user_input.lower() == 'q':
                print("正在停止服务器...")
                if server:
                    server.close_all() # 关闭所有连接并停止监听
                break
        except KeyboardInterrupt:
            # 允许 Ctrl+C 退出
            print("\n检测到 Ctrl+C，正在停止...")
            if server:
                server.close_all()
            break

    print("服务器已关闭。")
    sys.exit(0)

if __name__ == "__main__":
    main()
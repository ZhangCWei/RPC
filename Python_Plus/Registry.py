import time
import json
import socket
import threading

# 服务注册中心类
class ServiceRegistry:
    def __init__(self):
        self.services = {}
        self.service_status = {}

    # 注册服务
    def register_service(self, service_name, host, port):
        if service_name not in self.services:
            self.services[service_name] = []
            self.service_status[service_name] = {'status': 'active', 'last_heartbeat': time.time()}  # 初始化服务状态为活跃
        self.services[service_name].append((host, port))

    # 获取服务
    def get_service(self, service_name):
        if service_name in self.services:
            return self.services[service_name]
        else:
            return None

    # 更新服务状态
    def update_service_status(self, service_name, status):
        if service_name in self.service_status:
            self.service_status[service_name] = {'status': status, 'last_heartbeat': time.time()}

    # 移除超时的服务
    def remove_inactive_services(self):
        current_time = time.time()
        for service_name, status_info in self.service_status.items():
            if status_info['last_heartbeat'] is not None and current_time - status_info['last_heartbeat'] > 40:
                self.service_status[service_name] = {'status': 'inactive', 'last_heartbeat': None}


# 创建服务注册中心实例
service_registry = ServiceRegistry()

# 线程锁，用于保护服务注册中心的并发访问
registry_lock = threading.Lock()

# 注册中心服务器类
class RegistryServer:
    def __init__(self):
        # 创建套接字并绑定到本地主机的5000端口
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', 5000))
        self.sock.listen(5)

    # 处理客户端连接的方法
    def handle_client(self, client_sock, addr):
        # 接收客户端发送的数据
        data = client_sock.recv(1024)
        # 解析客户端请求的JSON数据
        request = json.loads(data.decode())
        # 处理不同类型的请求
        if request['type'] == 'register':
            # 如果是注册请求，获取服务名称、主机和端口，并注册服务到服务注册中心
            with registry_lock:
                service_name = request['service_name']
                host = request['host']
                port = request['port']
                service_registry.register_service(service_name, host, port)
                print(str(host) + ':' + str(port) + ' has been registered\n')
            # 发送成功响应给客户端
            response = {'status': 'success'}
        elif request['type'] == 'get_service':
            # 如果是获取服务请求，获取服务名称，并从服务注册中心获取服务列表
            with registry_lock:
                service_name = request['service_name']
                service = service_registry.get_service(service_name)
            # 构建响应数据，包括服务列表
            response = {'status': 'success', 'service': service}
        elif request['type'] == 'heartbeat':
            # 如果是心跳请求，更新服务状态为活跃
            with registry_lock:
                service_name = request['service_name']
                service_registry.update_service_status(service_name, 'active')
            # 发送成功响应给客户端
            response = {'status': 'success'}
        else:
            # 如果是无效的请求类型，返回错误响应
            response = {'status': 'error', 'message': 'Invalid request type'}
        # 将响应数据编码为JSON格式并发送给客户端
        client_sock.sendall(json.dumps(response).encode())
        # 关闭客户端套接字
        client_sock.close()

    # 定时打印活跃服务信息的方法
    def print_active_services(self):
        while True:
            time.sleep(40)  # 每隔60秒执行一次
            with registry_lock:
                print("Active Services:")
                service_registry.remove_inactive_services()  # 移除超时的服务
                for service_name, status in service_registry.service_status.items():
                    if status['status'] == 'active':
                        services = service_registry.get_service(service_name)
                        if services:
                            print("Service Name:", service_name)
                            for service in services:
                                print("--Host:", service[0], "Port:", service[1])
                print("~~··~~··~~··~~\n")

    # 监听客户端连接的方法
    def listen(self):
        # 输出提示信息，表示服务注册中心正在运行
        print("Registry server is running...\n")

        # 启动定时打印活跃服务信息的线程
        threading.Thread(target=self.print_active_services).start()

        while True:
            # 接受客户端连接
            client_sock, addr = self.sock.accept()
            # 创建线程处理客户端连接
            client_thread = threading.Thread(target=self.handle_client, args=(client_sock, addr))
            client_thread.start()

# 主函数
def main():
    # 创建注册中心服务器对象
    registry_server = RegistryServer()
    # 启动注册中心服务器监听客户端连接
    registry_server.listen()

# 如果作为独立程序运行，则调用主函数
if __name__ == "__main__":
    main()

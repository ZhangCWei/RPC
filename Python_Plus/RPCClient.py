import json
import socket
import argparse
import sys
import random


class TCP(object):
    def __init__(self):
        self.sock = None

    def connect(self, host, port):
        # 连接Server端
        try:
            addr_info = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
            for addr in addr_info:
                family, socktype, proto, _, sockaddr = addr
                try:
                    self.sock = socket.socket(family, socktype, proto)
                    self.sock.settimeout(5)  # 设置超时时间为5秒
                    self.sock.connect(sockaddr)
                    break
                except socket.timeout:
                    print("连接请求超时")
                    sys.exit(1)
                except socket.error:
                    if self.sock:
                        self.sock.close()
                    self.sock = None
                    continue
        except socket.gaierror:
            print("解析服务器地址失败")
            sys.exit(1)

        if not self.sock:
            print("无法连接到服务器")
            sys.exit(1)

    def send(self, data):
        # 将数据发送到Server端
        try:
            self.sock.sendall(data)
        except socket.error as e:
            print("发送数据错误:", str(e))
            sys.exit(1)

    def recv(self, length):
        # 接收Server端回传的数据
        try:
            self.sock.settimeout(30)  # 设置超时时间为10秒
            return self.sock.recv(length)
        except socket.timeout:
            print("接收数据超时")
            sys.exit(1)
        except socket.error as e:
            print("接收数据错误:", str(e))
            sys.exit(1)


class RPCClientStub(object):
    def __getattr__(self, function):
        def _func(*args):
            sdata = {'FuncName': function, 'Args': args}
            self.send(json.dumps(sdata).encode('utf-8'))  # 发送数据
            rdata = self.recv(1024)  # 接收方法执行后返回的结果
            result = json.loads(rdata.decode('utf-8'))  # 解析服务端返回的结果
            return result
        setattr(self, function, _func)
        return _func


class RPCClient(TCP, RPCClientStub):
    def __init__(self, registry_host, registry_port):
        super().__init__()
        self.registry_host = registry_host
        self.registry_port = registry_port
        # self.next_server_index = 0  # 用于记录下一个要选择的服务节点索引

    def choose_server(self, service_name):
        # 向注册中心请求获取服务节点列表
        try:
            registry_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            registry_sock.connect((self.registry_host, self.registry_port))
            request = {'type': 'get_service', 'service_name': service_name}
            registry_sock.sendall(json.dumps(request).encode())
            data = registry_sock.recv(1024)
            response = json.loads(data.decode())
            registry_sock.close()

            if response['status'] == 'success':
                # 从服务节点列表中随机选择一个节点
                service_nodes = response['service']
                if service_nodes:
                    # chosen_server = service_nodes[self.next_server_index]
                    # self.next_server_index = (self.next_server_index + 1) % len(service_nodes)
                    # return chosen_server
                    return random.choice(service_nodes)
                else:
                    print("没有可用的服务节点")
                    sys.exit(1)
            else:
                print("获取服务节点列表失败")
                sys.exit(1)
        except socket.error as e:
            print("与注册中心通信错误:", str(e))
            sys.exit(1)

    def connect_to_server(self, host, port):
        # 连接到选定的服务节点
        print("Connecting to server at {}:{}".format(host, port))
        self.connect(host, port)


def parse_arguments():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='RPC Client')
    parser.add_argument('-i', '--ip', type=str, help='Registry IP address (ipv4 or ipv6)', required=True)
    parser.add_argument('-p', '--port', type=int, help='Registry port', required=True)
    return parser.parse_args()


def main():
    args = parse_arguments()
    client = RPCClient(args.ip, args.port)
    service_name = 'RPCServer'  # 指定服务名称
    server_host, server_port = client.choose_server(service_name)
    client.connect_to_server(server_host, server_port)

    # 获取服务端提供的函数列表
    result = client.list()
    print("可用的函数列表：")
    print(result["result"])

    while True:
        # 提示用户输入所需的函数和参数
        user_input = input("请输入函数名和参数（空格分割）或输入 q 退出：")
        if user_input == 'q':
            break
        # 解析用户的输入
        input_list = user_input.split()
        if len(input_list) < 1:
            print("输入有误，请重新输入。")
            continue
        # 获取输入的函数名和参数
        function_name = input_list[0]
        function_args = input_list[1:]
        # 进行RPC通信
        if function_args is None:
            result = getattr(client, function_name)()
        else:
            result = getattr(client, function_name)(*function_args)
        print("返回值：", result["result"])


if __name__ == '__main__':
    main()

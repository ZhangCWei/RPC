import json
import socket
import argparse
import sys


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
            self.sock.settimeout(10)  # 设置超时时间为10秒
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
    pass


def parse_arguments():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='RPC Client')
    parser.add_argument('-i', '--ip', type=str, help='Server IP address (ipv4 or ipv6)', required=True)
    parser.add_argument('-p', '--port', type=int, help='Server port', required=True)
    return parser.parse_args()


def main():
    args = parse_arguments()
    client = RPCClient()
    client.connect(args.ip, args.port)
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

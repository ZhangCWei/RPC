import json
from socket import *
import threading
import argparse
import ServerFunction

function_lock = threading.Lock()


def handle_connection(server, conn, addr):
    while True:
        try:
            # 设置超时时间为5秒
            conn.settimeout(60)
            # 接收客户端数据，利用handle_msg处理，并返回
            msg = conn.recv(1024)
            if not msg:
                break
            # 处理接受的数据
            data = server.handle_msg(msg)
            # 回传处理后的数据给客户端
            try:
                conn.send(data)
            except timeout:
                print("发送响应数据超时")
                break
            except Exception as e:
                print("Error:", e)
                break
        except ConnectionResetError:
            print("客户端主动结束连接")
            break
        except timeout:
            print("读取客户端请求数据超时")
            break
        except Exception as e:
            print("Error:", e)
            break

    # 连接关闭
    conn.close()
    print("连接 {} 已关闭".format(str(addr)))


class TCP(object):
    # 初始化套接字
    def __init__(self):
        self.sock = socket(AF_INET6, SOCK_STREAM)  # 使用IPv6套接字

    # 绑定端口,进行监听
    def bind_and_listen(self, host, port):
        self.sock.setsockopt(IPPROTO_IPV6, IPV6_V6ONLY, 0)  # 启用IPv4和IPv6混合模式
        self.sock.bind((host, port))
        self.sock.listen(5)

    # 接收客户端连接，创建线程
    def accept_and_thread(self):
        # 等待接受客户端的连接
        conn, addr = self.sock.accept()
        # 提示新链接
        print("建立新的连接%s" % str(addr))
        # 创建一个新的线程，处理该客户端的连接
        thread = threading.Thread(target=handle_connection, args=(self, conn, addr))
        thread.start()


class RPCServerStub(object):
    def __init__(self):
        self.data = None

    def handle_method(self, data):
        # 将接收到的数据解码为 JSON 字符串
        self.data = json.loads(data.decode('utf-8'))
        # 获取方法名和参数
        func_name = self.data['FuncName']
        func_args = self.data['Args']

        # 调用相关函数
        with function_lock:
            try:
                if func_args is None:
                    result = ServerFunction.function_list[func_name]()
                else:
                    result = ServerFunction.function_list[func_name](*func_args)
                # 返回参数
                d = {'result': str(result)}
                return json.dumps(d).encode('utf-8')
            except Exception as e:
                print("调用映射服务的方法时出现异常:", e)
                # 返回错误
                d = {'result': 'Error'}
                return json.dumps(d).encode('utf-8')


class RPCServer(TCP, RPCServerStub):
    def __init__(self):
        TCP.__init__(self)
        RPCServerStub.__init__(self)

    def handle_msg(self, data):
        return self.handle_method(data)

    def listen_and_accept(self, host, port):
        self.bind_and_listen(host, port)
        print('正在监听 {}:{} 中...'.format(host, port))
        while True:
            try:
                self.accept_and_thread()
            except Exception as e:
                print("接收数据错误:", e)


def parse_arguments():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='RPC Server')
    parser.add_argument('-l', '--host', type=str, help='Server IP address (ipv4 or ipv6) to listen on', default='::')
    parser.add_argument('-p', '--port', type=int, help='Server port to listen on', required=True)
    return parser.parse_args()


def main():
    args = parse_arguments()
    server = RPCServer()
    server.listen_and_accept(args.host, args.port)


if __name__ == "__main__":
    main()

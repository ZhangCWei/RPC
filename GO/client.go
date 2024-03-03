package main

import (
	"bufio"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net"
	"os"
	"reflect"
	"time"
)

//// 服务列表格式
//type cserviceList struct {
//	FuncName   string // 函数名
//	FuncDetial string // 函数功能描述
//	ArgsDetial string // 函数参数描述
//}

// RPCData 定义 RPC 通信的数据格式
type cRPCData struct {
	FuncName string        // 访问的函数名
	Args     []interface{} // 函数的参数
}

func client(server_ip string, server_port string, server_name string, server_args []interface{}) {
	address := server_ip + ":" + server_port
	conn, err := net.DialTimeout("tcp", address, 5*time.Second)
	if err != nil {
		// 与服务端建立连接，导致的异常/超时
		fmt.Printf("Connect RPC server failed: %s\n", err)
		return
	}
	defer conn.Close()

	fmt.Println("连接RPC服务器成功")
	//data := new(RPCData)
	//data.FuncName = server_name
	//data.FuncNameLen = len(server_name)
	//data.Args = server_args
	uRPCdata := cRPCData{
		FuncName: server_name,
		Args:     server_args,
	}
	data, err := json.Marshal(uRPCdata) // JSON序列化
	if err != nil {
		// 序列化导致的异常/超时
		fmt.Printf("json marshal failed, err: %s\n", err)
		return
	}
	_, err = conn.Write(data) // 发送数据
	if err != nil {
		// 发送请求到服务端，写数据导致的异常
		fmt.Printf("client failed to write data, err: %s\n", err)
		return
	}

	// 获取服务器端返回的函数执行结果, 循环读取数据直到接收到完整的JSON数据。可以使用bufio.Reader来实现逐行读取数据，而不是一次性读取固定大小的数据。
	// 使用bufio.NewReader创建了一个reader来逐行读取数据
	reader := bufio.NewReader(conn)
	// 创建了一个json.Decoder并将其与reader关联
	decoder := json.NewDecoder(reader)
	// 解码的值赋值给response

	if server_name == "list" {
		// 打印服务列表
		// 通过decoder.Decode方法来解码数据，并将解码结果赋值给response变量
		var response = make(map[string]map[string]string)
		err = decoder.Decode(&response)
		if err != nil {
			// 从服务端接收响应时，读数据导致的异常/超时
			fmt.Printf("failed to decode response: %s\n", err)
			return
		}
		fmt.Println("服务列表：")
		for k, v := range response["result"] {
			fmt.Printf("函数名：%s; 所需参数：%s\n", k, v)
		}
	} else {
		// 返回服务调用结果
		// 解码的值赋值给response
		var response = make(map[string]string)
		err = decoder.Decode(&response)
		if err != nil {
			// 从服务端接收响应时，读数据导致的异常/超时
			fmt.Printf("failed to decode response: %s\n", err)
			return
		}
		fmt.Printf("%s\n", response["result"])
	}

}

// 发送报文，等待处理，接收报文所有阶段导致的超时
func timeListen(server_ip string, server_port string, server_name string, server_args []interface{}, ctx context.Context) error {
	client(server_ip, server_port, server_name, server_args)
	select {
	case <-ctx.Done():
		return errors.New("rpc client: call failed: " + ctx.Err().Error())
	}
}

func main() {
	//获取命令行参数
	//fmt.Println("命令行参数数量:", len(os.Args))
	//for k, v := range os.Args {
	//	fmt.Printf("args[%v]=[%v]\n", k, v)
	//}

	// 使用 context.WithTimeout 创建具备超时检测能力的 context 对象来控制
	ctx, _ := context.WithTimeout(context.Background(), 5*time.Second)
	if len(os.Args) >= 7 && os.Args[5] == "-s" && os.Args[7] == "-a" {
		// 输入的函数的参数
		args := os.Args[8:]
		Args := make([]reflect.Value, 0, len(os.Args))
		for _, uargs := range args {
			// 切片赋值可以用append()
			Args = append(Args, reflect.ValueOf(uargs))
		}

		uArgs := make([]interface{}, 0, len(Args))
		for _, a := range Args {
			if a.IsValid() {
				uArgs = append(uArgs, a.Interface())
			}
		}
		timeListen(os.Args[2], os.Args[4], os.Args[6], uArgs, ctx)
	} else if len(os.Args) == 6 && os.Args[5] == "-list" {
		// 服务发现
		timeListen(os.Args[2], os.Args[4], "list", nil, ctx)
	} else if os.Args[1] == "-h" {
		// 帮助参数
		fmt.Println("-i：客户端需要发送的服务端 ip 地址，需要同时支持 IPv4 和 IPv6，不得为空。")
		fmt.Println("-p：客户端需要发送的服务端端口，不得为空。")
		fmt.Println("-list：客户端服务发现。")
		fmt.Println("-s：客户端需要请求的服务名")
		fmt.Println("-a：客户端需要请求的服务所需要的参数")
		fmt.Println("-h：帮助参数，输出参数帮助。")
		fmt.Println("服务发现命令：go run client.go -i [服务器ip地址] -p [服务器RPC端口号] -list")
		fmt.Println("服务调用命令：go run client.go -i [服务器ip地址] -p [服务器RPC端口号] -s [请求的服务名] -a [依次输入所需参数]")
		fmt.Println("帮助：go run client.go -h")
	}
}

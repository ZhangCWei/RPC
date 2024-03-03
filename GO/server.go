package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net"
	"os"
	"reflect"
	"strconv"
)

// RPCData 定义 RPC 通信的数据格式
type sRPCData struct {
	FuncName string        // 函数名
	Args     []interface{} // 函数参数
}

// 组织服务的结构体
type MyService struct {
	funcs map[string]reflect.Value
	//serviceType string
}

// 服务的结构体的构造函数
func NewMyService() *MyService {
	return &MyService{
		funcs: make(map[string]reflect.Value),
		//serviceType: "",
	}
}

// 服务列表
// var mserviceList []serviceList
// 要初始化！！！
var mserviceList = make(map[string]string)

// 两个数相加
func (s *MyService) add(sarg1 string, sarg2 string) float64 {
	//s.serviceType = "num"
	arg1, _ := strconv.ParseFloat(sarg1, 64)
	arg2, _ := strconv.ParseFloat(sarg2, 64)
	result := arg1 + arg2
	fmt.Println("add！")
	return result
}

// 三个数相加
func (s *MyService) addd(sarg1 string, sarg2 string, sarg3 string) float64 {
	//s.serviceType = "num"
	arg1, _ := strconv.ParseFloat(sarg1, 64)
	arg2, _ := strconv.ParseFloat(sarg2, 64)
	arg3, _ := strconv.ParseFloat(sarg3, 64)
	result := arg1 + arg2 + arg3
	fmt.Println("addd！")
	return result
}

// 两个数相减
func (s *MyService) sub(sarg1 string, sarg2 string) float64 {
	arg1, _ := strconv.ParseFloat(sarg1, 64)
	arg2, _ := strconv.ParseFloat(sarg2, 64)
	result := arg1 - arg2
	fmt.Println("sub！")
	return result
}

// 两个数相乘
func (s *MyService) multi(sarg1 string, sarg2 string) float64 {
	arg1, _ := strconv.ParseFloat(sarg1, 64)
	arg2, _ := strconv.ParseFloat(sarg2, 64)
	result := arg1 * arg2
	fmt.Println("multi！")
	return result
}

// 求相反数
func (s *MyService) minus(sarg1 string) float64 {
	arg1, _ := strconv.ParseFloat(sarg1, 64)
	result := arg1 * -1
	fmt.Println("minus！")
	return result
}

// 求平方
func (s *MyService) square(sarg1 string) float64 {
	arg1, _ := strconv.ParseFloat(sarg1, 64)
	result := arg1 * arg1
	fmt.Println("square！")
	return result
}

// 求立方
func (s *MyService) cube(sarg1 string) float64 {
	arg1, _ := strconv.ParseFloat(sarg1, 64)
	result := arg1 * arg1 * arg1
	fmt.Println("cube！")
	return result
}

// 两个字符串单词拼接
func (s *MyService) joint(arg1 string, arg2 string) string {
	//s.serviceType = "string"
	result := arg1 + arg2
	fmt.Println("joint！")
	return result
}

// 打印
func (s *MyService) mprint(arg1 string) string {
	fmt.Println("mprint！")
	return arg1
}

// 判断整数的奇偶性
func (s *MyService) ParityJudge(sarg1 string) string {
	arg1, _ := strconv.Atoi(sarg1)
	fmt.Println("ParityJudge！")
	if arg1%2 == 0 {
		return "true"
	} else {
		return "false"
	}
}

// 判断一个数的正负
func (s *MyService) PNJudge(sarg1 string) string {
	arg1, _ := strconv.ParseFloat(sarg1, 64)
	fmt.Println("PNJudge！")
	if arg1 >= 0 {
		return "true"
	} else {
		return "false"
	}
}

// Register 注册需要 RPC 服务的函数， 通过反射机制实现函数名到函数的映射
func (s *MyService) Register(serviceName string, service interface{}, mFuncName string, mArgsDetail string) {
	// 已注册过则跳过
	if _, ok := s.funcs[serviceName]; ok {
		return
	}

	// 未注册过则注册
	// 在map中添加新的映射
	serviceVal := reflect.ValueOf(service)
	s.funcs[serviceName] = serviceVal
	// 在服务列表中添加新项
	mserviceList[mFuncName] = mArgsDetail
	//fmt.Println("服务注册！")
}

// 处理 RPC 服务的 conn 请求
func handleRPCRequest(conn net.Conn, service *MyService) {
	for {
		buf := make([]byte, 1024)
		n, err := conn.Read(buf)
		if err != nil {
			// 读客户端请求数据时，读数据导致的异常/超时
			log.Printf("read failed, err: %s\n", err)
			return
		}
		var uRPCData sRPCData
		err = json.Unmarshal(buf[:n], &uRPCData)
		if err != nil {
			// 反序列化导致的异常/超时
			log.Printf("failed to unmarshal RPC data: %s\n", err)
			return
		}
		//time.Sleep(10 * time.Second)

		if uRPCData.FuncName == "list" {
			// 服务发现，返回服务列表给客户端
			//fmt.Println("服务列表：")
			//for k, v := range mserviceList {
			//	fmt.Printf("函数名：%s; 所需参数：%s\n", k, v)
			//}
			var listMMap = make(map[string]map[string]string) // 为了不同语言通信需要而这么定义传回的数据
			listMMap["result"] = mserviceList
			data, err := json.Marshal(listMMap) // JSON序列化
			if err != nil {
				// 序列化导致的异常/超时
				log.Printf("json marshal failed, err: %s\n", err)
				return
			}
			_, err = conn.Write(data) // 发送数据
			if err != nil {
				// 发送相应数据时，写数据导致的异常/超时
				log.Printf("write failed, err: %s\n", err)
				return
			}
			fmt.Println("服务发现！")
		} else {
			// 获取函数
			serviceVal, ok := service.funcs[uRPCData.FuncName]
			if !ok {
				// 调用映射服务的方法时导致的异常/超时
				log.Printf("unexpected rpc call: function %s not exist", uRPCData.FuncName)
				return
			}
			// 获取参数
			uArgs := make([]reflect.Value, 0, len(uRPCData.Args))
			for _, arg := range uRPCData.Args {
				// 参数从命令行中获取，传进来前是string类型，直接将其转换为string类型传入函数中，由函数进行相应参数类型转换
				argVal := arg.(string)
				uArgs = append(uArgs, reflect.ValueOf(argVal))
			}

			// 通过反射动态调用方法
			returnVal := serviceVal.Call(uArgs)
			// 返回结果给客户端
			var replyMap = make(map[string]string)
			var reply string
			if uRPCData.FuncName == "add" || uRPCData.FuncName == "addd" || uRPCData.FuncName == "sub" || uRPCData.FuncName == "multy" || uRPCData.FuncName == "minus" || uRPCData.FuncName == "square" || uRPCData.FuncName == "cube" {
				re := fmt.Sprintf("%f", returnVal[0].Interface().(float64))
				reply = "the result is: " + re
				replyMap["result"] = reply
			} else if uRPCData.FuncName == "joint" || uRPCData.FuncName == "ParityJudge" || uRPCData.FuncName == "PNJudge" {
				reply = "the result is: " + returnVal[0].Interface().(string)
				replyMap["result"] = reply
			} else if uRPCData.FuncName == "mprint" {
				reply = returnVal[0].Interface().(string)
				replyMap["result"] = reply
			}

			// 返回函数执行结果给客户端
			data, err := json.Marshal(replyMap) // JSON序列化
			if err != nil {
				// 序列化导致的异常/超时
				log.Printf("json marshal failed, err: %s\n", err)
				return
			}
			_, err = conn.Write(data) // 发送数据
			if err != nil {
				// 返回数据给客户端时，写数据导致的异常/超时
				log.Printf("write failed, err: %s\n", err)
				return
			}
		}
	}

}

// 监听运行 RPC 服务
func (s *MyService) server(ip string, port string) error {
	address := ip + ":" + port
	//time.Sleep(10 * time.Second)	// 测试与服务端建立连接导致的超时
	listener, err := net.Listen("tcp", address) // 监听当前的tcp连接
	if err != nil {
		// 监听客户端时导致的异常/超时
		fmt.Printf("listen failed, err: %s\n", err)
		return err
	}
	// defer listener.Close()

	fmt.Println("Server started, listening on", address)
	//time.Sleep(10 * time.Second)

	for {
		conn, err := listener.Accept() // 建立连接
		if err != nil {
			// 与客户端建立连接时导致的异常/超时
			fmt.Printf("accept failed, err: %s\n", err)
			continue
		}
		// 协程并发通信
		go handleRPCRequest(conn, s)
	}
}

func main() {
	// 获取命令行参数
	//fmt.Println("命令行参数数量:", len(os.Args))
	//for k, v := range os.Args {
	//	fmt.Printf("args[%v]=[%v]\n", k, v)
	//}

	// 初始化一个服务结构体
	s := NewMyService()
	// 注册RPC服务
	s.Register("add", s.add, "add", "两个数字")
	s.Register("addd", s.addd, "addd", "三个数字")
	s.Register("sub", s.sub, "sub", "两个数字")
	s.Register("multi", s.multi, "multi", "两个数字")
	s.Register("minus", s.minus, "minus", "一个数字")
	s.Register("square", s.square, "square", "一个数字")
	s.Register("cube", s.cube, "cube", "一个数字")
	s.Register("joint", s.joint, "joint", "两个字符串单词")
	s.Register("mprint", s.mprint, "mprint", "一个需要打印的数字或者字符串单词")
	s.Register("ParityJudge", s.ParityJudge, "ParityJudge", "一个整数")
	s.Register("PNJudge", s.PNJudge, "PNJudge", "一个数字")

	if len(os.Args) >= 3 && os.Args[2] == "*" {
		// 启动服务器端广播监听
		s.server("0.0.0.0", os.Args[4])
	} else if len(os.Args) >= 3 && os.Args[2] != "*" {
		// 启动服务端监听某个指定ip
		s.server(os.Args[2], os.Args[4])
	} else if os.Args[1] == "-h" {
		// 帮助参数
		fmt.Println("-l：服务端监听的 ip 地址，需要同时支持 IPv4 和 IPv6，可以为空，默认监听所有 ip 地址，即 0.0.0.0。")
		fmt.Println("-p：服务端监听的端口号，不得为空。")
		fmt.Println("启动服务端：go run server.go -i [服务端监听的 ip 地址] -p [服务端监听的端口号]，若服务端监听的ip地址想为空，则对应位置输入*")
		fmt.Println("帮助：go run server.go -h")
	}
}

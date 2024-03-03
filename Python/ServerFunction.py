import inspect

function_list = {}
func_str = ""


def register_function(func):
    global func_str
    # 服务端方法注册
    name = func.__name__
    function_list[name] = func
    # 函数名与参数字典
    pars = inspect.signature(func).parameters
    args = ','.join(pars.keys())
    func_str += f"{name}({args});  "


@register_function
def list(num=0):
    print("客户端调用list()函数")
    return func_str


@register_function
def add(num1, num2):
    s = int(num1) + int(num2)
    print(s)
    return s


@register_function
def sub(num1, num2):
    s = int(num1) - int(num2)
    print(s)
    return s


@register_function
def multi(num1, num2):
    s = int(num1) * int(num2)
    print(s)
    return s


@register_function
def minus(num):
    s = -int(num)
    print(s)
    return s


@register_function
def square(num):
    print(int(num)*int(num))
    return int(num)*int(num)


@register_function
def cube(num):
    print(int(num) * int(num) * int(num))
    return int(num) * int(num) * int(num)


@register_function
def joint(str1, str2):
    st = str1 + str2
    print(st)
    return st


@register_function
def mprint(st):
    print(st)
    return st


@register_function
def ParityJudge(num):
    if int(num) % 2 == 0:
        print("true")
        return "true"
    else:
        print("false")
        return "false"


@register_function
def PNJudge(num):
    if int(num) >= 0:
        print("true")
        return "true"
    else:
        print("false")
        return "false"


from ast import List
import os
from random import choice
from openai import OpenAI
import json
from urllib.parse import quote
from dotenv import load_dotenv
import subprocess
import os
# 加载 .env 文件（通常放在项目根目录）
load_dotenv("/Users/maorongrong/workspace/python/learning-claude-code/env.local")

# 读取变量
api_key = os.environ.get("API_KEY")
base_url = os.environ.get("BASE_URL")
# 1. 系统提示词

# loop:
# call llm 提交用户提示词和系统提示词
# 当finish_reason=='use_tools'时，调用工具，并把调用信息追加到messages中，要让大模型知道它调用过工具，并把工具执行结果也追加到messages，让大模型知道工具执行结果
# 把content输出并追加到messages中，让大模型知道自己的最终输出结果
# 当finish_reason=='stop'时，用户输入提示词

# 我想要查看北京的天气,然后我想看看./Agent/s1.py中的内容
client = OpenAI(
    api_key=api_key,
    base_url=base_url,
)

THINK_OUTPUT = True

def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    # d 会遍历dangerous列表，如果有任意一个 d in command 为True any就会返回True
    # in 操作符可以判断字符串的匹配情况，以及列表是否含有某个元素
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(command, shell=True, cwd="/home",
                           capture_output=True, text=True, timeout=120)
        out = (r.stdout + r.stderr).strip()
        # python里面的三元表达式
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"

class todoManage:
    def __init__(self) -> None:
        # TODO列表
        self.items = []
    
    def update_todo(self, id: id, content: str, status: str, activeForm: str):
        # print(f"\n[系统日志] 正在调用todo管理工具修改/创建todo")
        for item in self.items:
            if id == item['id']:
                # 相同id，更新item数据
                item['content'] = content
                item['status'] = status
                item['activeForm'] = activeForm
                break
        else:
            # 新增
            self.items.append({
                "id": id,
                "status": status,
                "content": content,
                "activeForm": activeForm
            })
        self.render()
        return self.items
    
    def render(self) -> str:
        if not self.items:
            return "No todos."
        lines = []
        for item in self.items:
            marker = {"pending": "[ ]", "in_progress": "[>]", "completed": "[x]"}[item["status"]]
            lines.append(f"{marker} #{item['id']}: {item['activeForm']}")
        done = sum(1 for t in self.items if t["status"] == "completed")
        lines.append(f"\n({done}/{len(self.items)} completed)")
        result = "\n".join(lines)
        print(f"\r{result}", flush=True)
        #print(self.items)
        return 

TODO = todoManage()

# 声明工具 (Tool Declaration) - JSON Schema 格式
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取某个文件的全部内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件的完整路径，不能是目录名"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_bash",
            "description": "执行系统命令。",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "执行的命令。"
                    },
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_todo",
            "description": "在任务开始前你需要做一个计划，这个函数用于更新计划列表, 这个工具仅限你自己使用，不要暴露给用户。",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "计划条目的id, 修改现有计划状态和内容就传入已有的id, 新增就传入新的id"
                    },
                    "content": {
                        "type": "string",
                        "description": "计划的总标题"
                    },
                    "status": {
                        "type": "string",
                        "description": "该计划条目的状态, 有三种状态, 分别是: pending,in_progress,completed"
                    },
                    "activeForm": {
                        "type": "string",
                        "description": "该计划条目执行后的进度描述, 若还没有开始执行, 则传入一个预备的初始状态"
                    }
                },
                "required": ["id", "content", "status", "activeForm"]
            }
        }
    },
]


# 系统提示词
messages = [
    {"role": "system", "content": "你是一个得力助手，你在执行任务之前，要先使用update_todo创建一个任务列表，并在开始之前标记它为in_progress状态，在完成时标记它为done状态，在执行任务之前，你都必须更新这个todo列表，需要注意的是，如果有多个任务，你需要为每个任务都创建一个条目，也就是需要执行多次update_todo工具，在每次执行任务之前，你都必须先执行update_todo去更新相应任务的状态。"},
]

# 工具处理中心
TOOL_HANDLERS = {
    "get_weather":       lambda **kw: get_weather(kw["location"]),
    "read_file":  lambda **kw: read_file(kw["path"]),
    "update_todo":  lambda **kw: TODO.update_todo(int(kw["id"]), kw["content"], kw["status"], kw["activeForm"]),
    "run_bash": lambda **kw: run_bash(kw['command'])
}

# 工具函数
def get_weather(location: str):
    # print(f"\n[系统日志] 正在调用本地工具获取天气: {location}")
    # 真实场景下这里会请求天气API
    if "北京" in location:
        return '{"temperature": "999℃", "condition": "晴天"}'
    else:
        return '{"temperature": "未知", "condition": "未知"}'


def read_file(path):
    content = ""
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            content += line.strip()
    return content


class DictToObj:
    def __init__(self, d):
        for k, v in d.items():
            setattr(self, k, v)
result = DictToObj({"finish_reason": "stop"})

rounds_is_update_todo = 0
# Agent Loop
while True:
    # 超过三轮没有更新TODO，提醒大模型需要更新TODO列表
    if rounds_is_update_todo > 3:
        messages.append({
            "role": "user", "content": "请更新你的TODO列表。"
        })
    # 如果本轮结束，且没有调用工具的请求，则等待用户输入
    if result.finish_reason == "stop":
        userPrompt = ""
        userPrompt = input("\n>")
        # 用户输入的提示词作为第一条消息
        messages.append({
            "role": "user", "content": userPrompt
        })

    completion = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        stream=True
    )

    tool_calls = []
    resultContent = ""

    # 判断是否是新增的工具调用信息
    def isDeltaTool(tool_calls, index):
        if len(tool_calls) > index:
            return False
        else:
            return True

    # 这种语法是python中特有的，此时completion不是以往的存储在内存中的一个数组，而是一个流生成器（迭代器）
    # 每一次循环其实是等待生成器返回结果的一个过程，直到生成器请求的对象发出结束信号，循环才会结束
    # 这里的循环退出条件是有生成器决定的
    # 所以client.chat.completions.create()方法返回的是一个流生成器，这段逻辑其实是在持续的和服务器通信，接受大模型服务器的返回结果
    for chunk in completion:
        resultDelta = chunk.choices[0].delta
        result = chunk.choices[0]
        # 处理每一次大模型返回的结果
        # 判断有没有tool_calls
        if hasattr(resultDelta, "tool_calls") and resultDelta.tool_calls != None:
            # 如果有，判断是不是新的调用信息
            for item in resultDelta.tool_calls:
                if isDeltaTool(tool_calls, item.index):
                    # 新增一个工具调用
                    tool_calls.append({
                        "index": item.index,                     
                        "id": item.id,
                        "type": item.type,
                        "function": {
                            "name": item.function.name,
                            "arguments": ""
                        }
                    })
                else:
                    # 为现有的工具调用拼接参数
                    # 对象和dict不一样，对象可以用.来访问属性，dict只能通过key来访问属性
                    if item.function.arguments:
                        tool_calls[item.index]['function']['arguments'] += item.function.arguments
        
        # 输出思考内容
        if hasattr(resultDelta, "reasoning_content") and resultDelta.reasoning_content != None and THINK_OUTPUT:
            print(resultDelta.reasoning_content, end='', flush=True)
        if hasattr(result, "finish_reason") and result.finish_reason != None:
            if result.finish_reason == 'tool_calls':
                # 追加工具大模型自己输出的工具调用信息
                messages.append({
                    "role": "assistant",
                    "content": "", 
                    "tool_calls": tool_calls
                })
                # 调用工具
                for tool in tool_calls:
                    handler = TOOL_HANDLERS.get(tool['function']['name'])
                    arguments = json.loads(tool['function']['arguments'])
                    toolResult = "工具返回内容为空，请直接告诉用户，程序执行错误，并输出当前任务列表。"
                    try:
                        toolResult = handler(**arguments)
                    except Exception as e:
                        toolResult = f"工具执行出错: {str(e)}，请你检查自己的函数名/参数是否输出正确，如果没有问题，则提示用户。" 

                    toolResult = str(toolResult)
                    # 追加工具调用结果
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool['id'],
                        "name": tool['function']['name'],
                        "content": toolResult
                    })
                    

        # 输出最终结果
        if hasattr(resultDelta, "content") and resultDelta.content != None:
            print(resultDelta.content, end='', flush=True)
            resultContent += resultDelta.content

    # 追加模型输出的最终内容
    messages.append({
        "role": "assistant",
        "content": resultContent
    })


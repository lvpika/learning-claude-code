from ast import List
import os
from random import choice
from openai import OpenAI
import json
from urllib.parse import quote
from dotenv import load_dotenv
import prompts.prompt_repo
import tools.tool_defination as td
import utils.skills


# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 加载 .env 文件（放在脚本同级目录）
load_dotenv(os.path.join(SCRIPT_DIR, "env.local"))

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

messages = [
    {"role": "system", "content": prompts.prompt_repo.PARENT_SYSTEM_PROMPT},
]

# Agent Loop
def agent_loop():
    # print(tools.tools)
    class DictToObj:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k, v)
    result = DictToObj({"finish_reason": "stop"})

    rounds_is_update_todo = 0
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
        # if result.finish_reason == "tool_calls":
            # print("\r本轮结束，调用了工具，大模型开始分析工具结果")

        completion = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=td.PARENT_AGENT_TOOLS,
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
            # 判断有没有tool_calls，如果有的话说明开始返回工具调用相关的信息了
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
            # 大模型的一轮输出结束了，输出了结束信号
            if hasattr(result, "finish_reason") and result.finish_reason != None:
                # 结束理由是工具调用
                if result.finish_reason == 'tool_calls':
                    # 追加工具大模型自己输出的工具调用信息到上下文
                    messages.append({
                        "role": "assistant",
                        "content": "", 
                        "tool_calls": tool_calls
                    })
                    # 调用工具，大模型有可能会决定多次调用工具，所以要遍历tool_calls
                    for tool in tool_calls:
                        handler = td.TOOL_HANDLERS.get(tool['function']['name'])
                        arguments = json.loads(tool['function']['arguments'])
                        toolResult = "工具返回内容为空，请直接告诉用户，程序执行错误，并输出当前任务列表。"
                        try:
                            toolResult = handler(**arguments)
                        except Exception as e:
                            toolResult = f"工具执行出错: {str(e)}，请你检查自己的函数名/参数是否输出正确，如果没有问题，则提示用户。" 

                        toolResult = str(toolResult)
                        # 追加工具调用结果到上下文
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool['id'],
                            "name": tool['function']['name'],
                            "content": toolResult
                        })
                        
            # 大模型输出的给用户内容
            if hasattr(resultDelta, "content") and resultDelta.content != None:
                print(resultDelta.content, end='', flush=True)
                # 这里的ressultContent应该每一轮都要重置才对，不然每次追加到上下文的信息都包括前几轮的内容
                resultContent += resultDelta.content

        # 追加模型输出给用户的内容到上下文
        messages.append({
            "role": "assistant",
            "content": resultContent
        })


if __name__ == "__main__":
    agent_loop()


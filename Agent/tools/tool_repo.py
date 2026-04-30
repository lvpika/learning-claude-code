
# 工具函数
from ntpath import isdir
from openai.types.chat.chat_completion_content_part_param import File
from ast import List
import os
from random import choice
from openai import OpenAI
import json
from urllib.parse import quote
from dotenv import load_dotenv
import prompts.prompt_repo
import tools.tool_defination as td
import pathlib
import os


def run_sub_agent(prompt: str) -> str:
    print(f"\r调用了子Agent：${prompt}")
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(SCRIPT_DIR, "env.local"))
    api_key = os.environ.get("API_KEY")
    base_url = os.environ.get("BASE_URL")
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )
    result = {}

    # print(api_key, base_url)
    # 新的干净的上下文列表
    sub_message = [{"role": "system", "content": prompts.prompt_repo.SUB_AGENT_PROMPT}, {"role": "user", "content": prompt}]
    # 子Agent最多循环30次
    
    
    for _ in range(30):
        tool_calls = []
        # 当字Agent输出结束信号后，返回结果给父Agent
        if hasattr(result, 'finish_reason') and result.finish_reason != None and result.finish_reason == 'stop':
            print("子Agent退出")
            # print(resultContent)
            # print(sub_message)
            return resultContent
        # 这个resultContent要放到返回结果的下方，不然返回前会被置空
        resultContent = ""
        completion = client.chat.completions.create(
            model="deepseek-chat",
            messages=sub_message,
            tools=td.SUB_AGENT_TOOLS,
            stream=True
        )

        def isDeltaTool(tool_calls, index):
            if len(tool_calls) > index:
                return False
            else:
                return True

        for chunk in completion:
            resultDelta = chunk.choices[0].delta
            result = chunk.choices[0]
            if hasattr(resultDelta, "tool_calls") and resultDelta.tool_calls != None:
                for item in resultDelta.tool_calls:
                    if isDeltaTool(tool_calls, item.index):
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
                        if item.function.arguments:
                            tool_calls[item.index]['function']['arguments'] += item.function.arguments
            # if hasattr(resultDelta, "reasoning_content") and resultDelta.reasoning_content != None and THINK_OUTPUT:
            #     print(resultDelta.reasoning_content, end='', flush=True)
            if hasattr(result, "finish_reason") and result.finish_reason != None:
                if result.finish_reason == 'tool_calls':
                    sub_message.append({
                        "role": "assistant",
                        "content": "", 
                        "tool_calls": tool_calls
                    })
                    for tool in tool_calls:
                        handler = td.TOOL_HANDLERS.get(tool['function']['name'])
                        arguments = json.loads(tool['function']['arguments'])
                        toolResult = "工具返回内容为空，请直接输出程序执行错误。"
                        try:
                            toolResult = handler(**arguments)
                        except Exception as e:
                            toolResult = f"工具执行出错: {str(e)}，请你检查自己的函数名/参数是否输出正确，如果没有问题，则输出工具调用出错。" 

                        toolResult = str(toolResult)
                        sub_message.append({
                            "role": "tool",
                            "tool_call_id": tool['id'],
                            "name": tool['function']['name'],
                            "content": toolResult
                        })
            if hasattr(resultDelta, "content") and resultDelta.content != None:
                resultContent += resultDelta.content

        sub_message.append({
            "role": "assistant",
            "content": resultContent
        })


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



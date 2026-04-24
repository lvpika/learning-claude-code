
# 工具函数
from openai.types.chat.chat_completion_content_part_param import File
import subprocess

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



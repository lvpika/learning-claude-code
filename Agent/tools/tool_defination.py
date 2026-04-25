import tools.tool_repo as tools_module
# 工具处理中心
TOOL_HANDLERS = {
    "get_weather":  lambda **kw: tools_module.get_weather(kw["location"]),
    "read_file":    lambda **kw: tools_module.read_file(kw["path"]),
    "update_todo":  lambda **kw: tools_module.TODO.update_todo(int(kw["id"]), kw["content"], kw["status"], kw["activeForm"]),
    "run_bash":     lambda **kw: tools_module.run_bash(kw["command"]),
    "run_sub_agent":     lambda **kw: tools_module.run_sub_agent(kw["prompt"])
}

# 工具声明 (Tool Declaration) - JSON Schema 格式
PARENT_AGENT_TOOLS = [
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
    {
        "type": "function",
        "function": {
            "name": "run_sub_agent",
            "description": "当你需要执行一个很大的任务时，你只需要统筹任务执行计划，具体的任务你要分配给子Agent去执行，保持你的上下文干净，当用户主动要求你使用子Agent时你也要调用这个工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "你给子Agent分配的任务的描述，尽量步骤清晰，目的明确，你想要的结果也需要描述。"
                    }
                },
                "required": ["prompt"]
            }
        }
    },
]

SUB_AGENT_TOOLS = [
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
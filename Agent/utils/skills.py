import os
import pathlib
import re
def skill_directory():
    """
        返回技能仓库dict

        Args: self

        Returns: [
            {
                "meta": {
                    "name": skill_name
                    "description": skill_description
                    "argument-hint": skill_argument_hint
                    "allowed-tools": skill_allowed_tools
                    "path": skill_file_path
                },
                "content": skill_content
            }
        ]
    """
    work_path = os.getcwd()
    skill_repo_path = os.path.join(work_path, "Agent", "skills")
    skill_tree = pathlib.Path(skill_repo_path)
    # 所有skill列表
    result = []
    # 获取所有子目录
    for subdir in skill_tree.iterdir():
        if subdir.is_dir():
            # 读取目录下所有文件
            for file in subdir.rglob("SKILL.md"):
                if file.is_file():
                    skill_item = {}
                    skill_header = {}
                    content = file.read_text(encoding="utf-8")
                    skill_head_match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
                    # 处理这个skill的摘要信息
                    for line in skill_head_match.group(1).splitlines():
                        key, value = line.split(":")
                        skill_header[key] = value
                    skill_header["path"] = os.path.join(work_path, "Agent", "skills", subdir.name, file.name)
                    skill_item["meta"] = skill_header
                    skill_item["content"] = skill_head_match.group(2)
                    result.append(skill_item)
    return result

from urllib.parse import quote
class todoManage:
    # TODO列表
    items: list[dict] = []
    def update_todo(self, id: id, content: str, status: str, activeForm: str):
        print(f"\n[系统日志] 正在调用todo管理工具修改/创建todo")
        for item in todoManage.items:
            if id == item.id:
                # 相同id，更新item数据
                item.content = content
                item.status = status
                item.activeForm = activeForm
            break
        else:
            # 新增
            todoManage.items.append({
                "id": id,
                "status": status,
                "content": content,
                "activeForm": activeForm
            })
    
    def render(self) -> str:
        if not todoManage.items:
            return "No todos."
        lines = []
        for item in todoManage.items:
            marker = {"pending": "[ ]", "in_progress": "[>]", "completed": "[x]"}[item["status"]]
            lines.append(f"{marker} #{item['id']}: {item['activeForm']}")
        done = sum(1 for t in todoManage.items if t["status"] == "completed")
        lines.append(f"\n({done}/{len(todoManage.items)} completed)")
        return "\n".join(lines)

TODO = todoManage()

TODO.update_todo(1, "查看天气", "pending", "查看天气中....")
print(TODO.render())


print(quote("工具执行出错: 'dict' object has no attribute 'id'，请你检查自己的函数名/参数是否输出正确，如果没有问题，则提示用户。"))
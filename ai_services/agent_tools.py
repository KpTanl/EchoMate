from datetime import datetime
import subprocess
import os

class AgentTool:
    """Agent 工具基类"""
    @property
    def name(self) -> str:
        return "base_tool"
        
    @property
    def description(self) -> str:
        return "基类工具，无实际功能"

    def execute(self, **kwargs) -> str:
        raise NotImplementedError()


class TimeTool(AgentTool):
    """获取当前时间的工具"""
    @property
    def name(self) -> str:
        return "get_current_time"
        
    @property
    def description(self) -> str:
        return "获取系统当前的真实时间和日期"

    def execute(self, **kwargs) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class NotepadTool(AgentTool):
    """打开记事本的工具"""
    @property
    def name(self) -> str:
        return "open_notepad"
        
    @property
    def description(self) -> str:
        return "在 Windows 上帮你打开一个全新的记事本程序"

    def execute(self, **kwargs) -> str:
        try:
            if os.name == 'nt':
                subprocess.Popen(['notepad.exe'])
                return "已成功为您打开记事本！"
            return "当前系统不支持打开记事本。"
        except Exception as e:
            return f"打开记事本失败: {e}"

# 预留给外部引用的装配列表
available_tools = [
    TimeTool(),
    NotepadTool()
]

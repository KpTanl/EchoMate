import ast
import json
import re
from collections import deque
from typing import Deque, Dict, List, Optional, Any

from PySide6.QtCore import QThread, Signal, QObject

from ai_services.cloud_llm_api import cloud_llm
from core.config import config
from core.event_bus import event_bus
from core.memory_manager import memory_manager


class LLMWorker(QThread):
    finished_signal = Signal(str)

    def __init__(self, messages: List[Dict[str, str]]):
        super().__init__()
        self.messages = messages

    def run(self):
        # Blocking API call runs in worker thread, not UI thread.
        if config.model_mode == "cloud":
            response = cloud_llm.generate(self.messages)
            self.finished_signal.emit(response)
        else:
            self.finished_signal.emit("Local LLM not fully implemented yet.")


class BaseAgent(QObject):
    """
    基础任务调度器，提供独立队列与处理循环，避免竞态
    """
    def __init__(self):
        super().__init__()
        self.is_running = False
        self._queue: Deque[Any] = deque()
        self._inflight = False
        self._workers: List[LLMWorker] = []

    def start(self):
        self.is_running = True

    def stop(self):
        self.is_running = False
        self._queue.clear()
        self._inflight = False
        for worker in self._workers:
            worker.quit()
            worker.wait(100)
        self._workers.clear()

    def enqueue(self, task: Any):
        self._queue.append(task)
        self._process_next()

    def _process_next(self):
        if not self.is_running or self._inflight or not self._queue:
            return

        task = self._queue.popleft()
        self._inflight = True
        self._execute_task(task)

    def _execute_task(self, task: Any):
        # To be overridden by subclasses
        pass

    def _cleanup_workers(self):
        self._workers = [w for w in self._workers if not w.isFinished()]

    def _finish_task(self):
        self._inflight = False
        self._cleanup_workers()
        self._process_next()

    def _extract_tag(self, text: str, tag_name: str) -> tuple[str, str]:
        pattern = rf"\[{re.escape(tag_name)}:\s*(.*?)\]"
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        cleaned_text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL).strip()
        value = match.group(1).strip() if match else ""
        return cleaned_text, value


class FastAgent(BaseAgent):
    """
    快系统实体：专注接管所有实时反馈、UI显示更新以及普通聊天请求。
    """
    def __init__(self, manager: "AgentEngine", max_history: int = 10):
        super().__init__()
        self.manager = manager
        self.max_history = max_history
        self.conversation_history: List[Dict[str, str]] = []

    def _create_base_context(self) -> str:
        return self.manager.create_base_context()

    def _build_fast_prompt(self, event_data: Dict[str, object]) -> str:
        fast_memory = memory_manager.get_all_memories_text(scope="fast_agent")
        return self._create_base_context() + (
            f"【快系统独立记忆】\n{fast_memory}\n"
            f"【快系统当前情绪基底】{self.manager.fast_emotion}\n"
            f"主人刚刚对你做了动作：{event_data.get('system_note', '未知动作')}。\n"
            "你是快系统：请立刻用一两句短话回应，不要长篇思考。\n"
            "如果需要记录快系统记忆，末尾单独一行输出 [FAST_MEMORY: 记忆内容]。\n"
            "如果这次反应改变了快系统情绪，末尾单独一行输出 [FAST_STATE: 新情绪]。\n"
            "除了上述标签，不要输出任何额外前缀。"
        )

    def _build_chat_prompt(self) -> str:
        shared_memory = memory_manager.get_all_memories_text(scope="shared")
        return self._create_base_context() + (
            f"【共享长期记忆】\n{shared_memory}\n\n"
            f"【当前慢系统情绪基底】{self.manager.slow_emotion}\n"
            "【工作指令】\n"
            "1. 坚守小鸟身份，用生动、简短、可爱的语气回答主人。\n"
            "2. 若需记下共享记忆，末尾请单独一行输出 [MEMORY: 事实内容]。"
        )

    def _execute_task(self, task: Dict[str, Any]):
        task_type = task.get("type")

        if task_type == "chat":
            text = task.get("text", "")
            self.conversation_history.append({"role": "user", "content": text})
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]

            prompt = self._build_chat_prompt()
            messages = [{"role": "system", "content": prompt}] + self.conversation_history
            worker = LLMWorker(messages)
            worker.finished_signal.connect(self._on_chat_finished)
            worker.finished_signal.connect(worker.deleteLater)
            self._workers.append(worker)
            worker.start()

        elif task_type == "fast_event":
            event_data = task.get("event_data", {})
            prompt = self._build_fast_prompt(event_data)
            messages = [{"role": "user", "content": prompt}]
            worker = LLMWorker(messages)
            worker.finished_signal.connect(self._on_fast_event_finished)
            worker.finished_signal.connect(worker.deleteLater)
            self._workers.append(worker)
            worker.start()

    def _on_chat_finished(self, response: str):
        try:
            display_text, shared_memory = self._extract_tag(response, "MEMORY")

            if shared_memory:
                memory_manager.add_memory(shared_memory, scope="shared")

            self.conversation_history.append({"role": "assistant", "content": display_text})
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]

            event_bus.on_agent_response.emit(display_text)
        finally:
            self._finish_task()

    def _on_fast_event_finished(self, response: str):
        try:
            display_text, fast_memory = self._extract_tag(response, "FAST_MEMORY")
            display_text, fast_state = self._extract_tag(display_text, "FAST_STATE")

            if fast_memory:
                memory_manager.add_memory(fast_memory, scope="fast_agent")

            if fast_state:
                self.manager.fast_emotion = fast_state

            if display_text:
                event_bus.on_agent_response.emit(display_text)
        finally:
            self._finish_task()


class SlowAgent(BaseAgent):
    """
    慢系统实体：专注后台异步串行反思，根据设定其输出将长远影响小鸟的状态和心情。
    """
    def __init__(self, manager: "AgentEngine"):
        super().__init__()
        self.manager = manager

    def _create_base_context(self) -> str:
        return self.manager.create_base_context()

    def _build_slow_prompt(self, task: Dict[str, Any]) -> str:
        slow_memory = memory_manager.get_all_memories_text(scope="slow_agent")
        
        task_type = task.get("type")
        if task_type == "slow_event":
            event_data = task.get("event_data", {})
            event_desc = f"事件：{event_data.get('system_note', '未知动作')}。短时间频率：{event_data.get('frequency', 'unknown')}。"
        else:
            text = task.get("text", "")
            event_desc = f"刚刚主人对你说了一句话：\"{text}\"。"

        return self._create_base_context() + (
            f"【慢系统独立记忆】\n{slow_memory}\n"
            f"【慢系统当前情绪基底】{self.manager.slow_emotion}\n"
            f"{event_desc}\n"
            "你是慢系统：请简要输出 10-150 字内心独白，重点是长期的情绪与感受变化，且只需要讨论必要的内容，不用太加戏，这是后台的内容。\n"
            "末尾必须单独输出一行 [SLOW_STATE: 新情绪基底]，这将决定小鸟接下来的长远态度和心情。\n"
            "如果需要记录慢系统记忆，再额外输出一行 [SLOW_MEMORY: 记忆内容]。"
        )

    def _execute_task(self, task: Dict[str, Any]):
        prompt = self._build_slow_prompt(task)
        messages = [{"role": "user", "content": prompt}]
        worker = LLMWorker(messages)
        worker.finished_signal.connect(self._on_slow_event_finished)
        worker.finished_signal.connect(worker.deleteLater)
        self._workers.append(worker)
        worker.start()

    def _on_slow_event_finished(self, response: str):
        try:
            cleaned_text, slow_memory = self._extract_tag(response, "SLOW_MEMORY")
            cleaned_text, slow_state = self._extract_tag(cleaned_text, "SLOW_STATE")

            if slow_memory:
                memory_manager.add_memory(slow_memory, scope="slow_agent")

            if slow_state:
                self.manager.slow_emotion = slow_state

            from datetime import datetime
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(
                f"\n[{ts}] [Agent 慢系统反思完毕]"
                f"\n完整内心独白:\n{cleaned_text.strip()}"
                f"\n--> 慢系统新情绪基底: 【{self.manager.slow_emotion}】\n"
            )
        finally:
            self._finish_task()


class AgentEngine(QObject):
    """
    引擎协调器：统筹初始化、启停以及底层状态的分发。
    真正的工作量分配给互相独立、带有单独队列的 FastAgent 和 SlowAgent。
    """
    def __init__(self, max_history: int = 10):
        super().__init__()
        self.current_action = "sleeping"
        self.is_in_cage = True

        # 挂载共享环境与情绪状态
        self.fast_emotion = "平静"
        self.slow_emotion = "平静"

        # 实例化完全独立的俩Agent子系统
        self.fast_agent = FastAgent(self, max_history)
        self.slow_agent = SlowAgent(self)

        event_bus.on_user_input.connect(self._handle_user_input)
        event_bus.on_state_change.connect(self._on_state_change)

    def _on_state_change(self, state_data: dict):
        self.current_action = state_data.get("action", "sleeping")
        self.is_in_cage = state_data.get("in_cage", True)

    def start(self):
        self.fast_agent.start()
        self.slow_agent.start()

    def stop(self):
        self.fast_agent.stop()
        self.slow_agent.stop()

    def create_base_context(self) -> str:
        location_str = "在笼子里" if self.is_in_cage else "在主人的桌面上"
        action_map = {
            "sleeping": "正在闭着眼睛睡觉休息",
            "idle": "静静地发呆或闲逛",
            "flying": "正扑腾着翅膀飞来飞去",
            "curious": "正歪着头，充满好奇地看着发生的事",
        }
        action_str = action_map.get(self.current_action, "正在待命")

        return (
            f"你是一个可爱的桌面宠物小鸟，主人的专属伙伴，名字叫{config.pet_name}。\n"
            f"属性：性别 {config.pet_gender}，生日 {config.pet_birthday}，喜好 {config.pet_likes}，讨厌 {config.pet_dislikes}。\n"
            f"当前情境：位置 {location_str}，动作 {action_str}。\n"
        )

    def _parse_system_event(self, text: str) -> Optional[Dict[str, object]]:
        if not text or not text.startswith("{"):
            return None

        data: Optional[object] = None
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            try:
                data = ast.literal_eval(text)
            except (ValueError, SyntaxError):
                return None

        if isinstance(data, dict) and "event_type" in data:
            return data

        return None

    def _handle_user_input(self, text: str):
        event_data = self._parse_system_event(text)
        if event_data is not None:
            # 高频动作触发时，独立分发任务到两边队列
            self.fast_agent.enqueue({"type": "fast_event", "event_data": event_data})
            self.slow_agent.enqueue({"type": "slow_event", "event_data": event_data})
        else:
            # 纯文本聊天专门交由快系统处理，同时也推入慢系统排队反思
            self.fast_agent.enqueue({"type": "chat", "text": text})
            self.slow_agent.enqueue({"type": "slow_chat", "text": text})


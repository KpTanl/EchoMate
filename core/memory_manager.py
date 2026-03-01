import json
import os
from typing import Dict, List


class MemoryManager:
    """Manage persistent memories with independent scopes."""

    def __init__(self):
        self._memory_file = os.path.join(os.path.dirname(__file__), "..", "memory.json")
        self.memories: Dict[str, List[str]] = {
            "shared": [],
            "fast_agent": [],
            "slow_agent": [],
        }
        self.load()

    def load(self):
        if not os.path.exists(self._memory_file):
            return

        try:
            with open(self._memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.memories = self._normalize_payload(data)
        except Exception as e:
            print(f"长期记忆读取失败: {e}")
            self.memories = {
                "shared": [],
                "fast_agent": [],
                "slow_agent": [],
            }

    def save(self):
        data = {"memories": self.memories}
        try:
            with open(self._memory_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"长期记忆保存失败: {e}")

    def _normalize_payload(self, data: object) -> Dict[str, List[str]]:
        normalized = {
            "shared": [],
            "fast_agent": [],
            "slow_agent": [],
        }

        if not isinstance(data, dict):
            return normalized

        raw_memories = data.get("memories")
        if isinstance(raw_memories, dict):
            for scope in normalized:
                items = raw_memories.get(scope, [])
                if isinstance(items, list):
                    normalized[scope] = [str(item).strip() for item in items if str(item).strip()]
            return normalized

        # Backward compatibility with old schema.
        legacy_items = data.get("long_term_memories", [])
        if isinstance(legacy_items, list):
            normalized["shared"] = [str(item).strip() for item in legacy_items if str(item).strip()]

        return normalized

    def add_memory(self, memory_text: str, scope: str = "shared"):
        """Add a new memory item and persist it."""
        memory_text = memory_text.strip()
        if not memory_text:
            return

        if scope not in self.memories:
            scope = "shared"

        if memory_text not in self.memories[scope]:
            self.memories[scope].append(memory_text)
            self.save()

    def get_all_memories_text(self, scope: str = "shared") -> str:
        """Get formatted memory text for prompt injection."""
        if scope not in self.memories:
            scope = "shared"

        scoped_memories = self.memories.get(scope, [])
        if not scoped_memories:
            return "目前还没有记住任何特别的事情。"

        return "\n".join([f"- {m}" for m in scoped_memories])


memory_manager = MemoryManager()

import json
import time

from PySide6.QtCore import QObject, QTimer

from core.event_bus import event_bus


class StateManager(QObject):
    """Core finite state machine for pet interactions."""

    def __init__(self):
        super().__init__()
        self.current_state = "sleeping"
        self.is_in_cage = True

        self.state_timer = QTimer(self)
        self.state_timer.setSingleShot(True)
        self.state_timer.timeout.connect(self._restore_default_state)

        event_bus.on_toggle_cage.connect(self._on_toggle_cage)
        event_bus.on_pet_clicked.connect(self._on_pet_clicked)
        event_bus.on_pet_rubbed.connect(self._on_pet_rubbed)
        event_bus.on_user_input.connect(self._on_user_input)
        event_bus.on_agent_response.connect(self._on_agent_response)

        self.interaction_history = []
        self.long_term_interaction_history = []

    def _change_state(self, new_state: str, duration: int = 0):
        self.current_state = new_state
        event_bus.on_state_change.emit({"action": self.current_state, "in_cage": self.is_in_cage})

        if duration > 0:
            self.state_timer.start(duration)
        else:
            self.state_timer.stop()

    def _restore_default_state(self):
        if self.is_in_cage:
            self._change_state("sleeping")
        else:
            self._change_state("idle")

    def _on_toggle_cage(self, show_cage: bool):
        self.is_in_cage = show_cage
        self._restore_default_state()

    def _check_interaction_limit(self) -> str:
        now = time.time()

        self.interaction_history = [t for t in self.interaction_history if now - t <= 30]
        self.long_term_interaction_history = [t for t in self.long_term_interaction_history if now - t <= 60]

        if self.interaction_history:
            last_time = self.interaction_history[-1]
            if now - last_time < 3:
                return "ignore"

        self.long_term_interaction_history.append(now)

        if len(self.long_term_interaction_history) >= 8:
            return "fly_away"

        if len(self.interaction_history) >= 5:
            return "angry"

        self.interaction_history.append(now)
        return "normal"

    def _emit_system_event(self, event_type: str, frequency: str, note: str):
        event_info = {
            "event_type": event_type,
            "frequency": frequency,
            "is_in_cage": self.is_in_cage,
            "current_state": self.current_state,
            "system_note": note,
        }
        event_bus.on_user_input.emit(json.dumps(event_info, ensure_ascii=False))

    def _on_pet_clicked(self):
        status = self._check_interaction_limit()
        if status == "ignore":
            return

        if status == "fly_away":
            event_bus.on_toggle_cage.emit(True)
            return

        if status == "angry":
            self._change_state("angry", 2000)
            self._emit_system_event("poke", "high", "疯狂戳击")
            return

        self._change_state("curious", 2000)
        self._emit_system_event("poke", "normal", "轻轻戳了一下")

    def _on_pet_rubbed(self):
        status = self._check_interaction_limit()
        if status == "ignore":
            return

        if status == "fly_away":
            event_bus.on_toggle_cage.emit(True)
            return

        if status == "angry":
            self._change_state("angry", 2000)
            self._emit_system_event("rub", "high", "疯狂来回摸")
            return

        self._change_state("happy", 2000)
        self._emit_system_event("rub", "normal", "温柔地抚摸")

    def _on_user_input(self, text: str):
        self._change_state("curious")

    def _on_agent_response(self, text: str):
        self._change_state("curious", 3000)


state_manager = StateManager()

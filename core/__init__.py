# core 模块向外暴露的核心单例
from .event_bus import event_bus
from .config import config
from .state_manager import state_manager
from .mod_loader import mod_loader
from .app import app_manager

__all__ = [
    'event_bus',
    'config',
    'state_manager',
    'mod_loader',
    'app_manager'
]

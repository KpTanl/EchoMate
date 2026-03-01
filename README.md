# EchoMate

基于 Python 和 PySide6 的模块化桌面宠物框架。采用 MVC 架构，设计为高可扩展的本地与云端 AI 结合的智能小助手。

## 🌟 核心特色与设计理念

- **无边框透明交互**：提供沉浸式的桌面宠物体验，宠物可以在桌面随意拖拽、飞行，并拥有生动的动画。
- **解耦的系统架构**：严格分离展示层（PySide6）、核心逻辑状态管理以及第三方接口抽象。借助集中式的事件总线（Event Bus）进行模块间的消息传递。
- **快慢双系统 (Dual-Agent System)**：核心逻辑由两个相互独立的 Agent 队列组成：
  - **快系统 (Fast Agent)**：处理实时事件（如抚摸、点击）和普通聊天，保证秒级内返回，给主人提供实时的交互反馈。
  - **慢系统 (Slow Agent)**：负责在后台进行异步、深度的内心反思（Inner Monologue），其实际反思结果将悄然改变小鸟的长远情感基底与行为模式。这使得宠物不仅是工具，更是一个“拥有生命和成长轨迹”的智能体。

## 📂 项目结构

- `core/`：智能体双系统与核心逻辑，包括 `agent_engine.py` (双系统调度)、`state_manager.py` (状态机)、`memory_manager.py` (记忆存储) 和 `event_bus.py`。
- `ui/`：所有视觉呈现部分，包括 `main_window.py` (操作面板与宠物笼)、`pet_window.py` (高自由度的桌面自由飞行视图) 以及 `tray_menu.py` (系统托盘)。
- `ai_services/`：外部大模型 API 的调用抽象，如 `cloud_llm_api.py`。
- `assets/`：动画序列帧及相关图像资源。
- `根目录脚本`：包含如 `remove_bg.py` 和 `process_images.py` 等用于处理图片背景和批量自动化工具脚本。

## 🛠️ 技术栈

- Python 3.10+
- PySide6 (UI 与底层事件循环)
- requests (网络请求)
- Pillow & rembg (图片背景去除与处理)

## 🚀 快速开始

### 1. 创建并激活虚拟环境 (推荐)
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.\.venv\Scripts\Activate.ps1
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行
```bash
python main.py
```

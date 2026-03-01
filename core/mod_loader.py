class ModLoader:
    """
    第三方模块/插件加载器 (Dummy)
    后期可以用 importlib 实现热插拔加载。
    """
    def __init__(self):
        self.loaded_mods = {}

    def load_all(self):
        pass
        
mod_loader = ModLoader()

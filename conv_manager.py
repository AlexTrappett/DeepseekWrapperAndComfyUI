# conv_manager.py
import os, json
from prompts import FLUX_RULES, WTBOY_RULES

class ConversationManager:
    def __init__(self, store_dir="conversations"):
        os.makedirs(store_dir, exist_ok=True)
        self.store_dir = store_dir
        self.histories = {}

    def _path(self, name):
        return os.path.join(self.store_dir, f"{name}.json")

    def load(self, name):
        path = self._path(name)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.histories[name] = json.load(f)
        else:
            if name.startswith("flux-"):
                system = {"role": "system", "content": FLUX_RULES}
            elif name.startswith("wtboy-"):
                system = {"role": "system", "content": WTBOY_RULES}
            else:
                system = {"role": "system", "content": "You are a helpful assistant."}
            self.histories[name] = [system]
        return self.histories[name]

    def save(self, name):
        with open(self._path(name), "w", encoding="utf-8") as f:
            json.dump(self.histories[name], f, indent=2)

    def append(self, name, role, content):
        if name not in self.histories:
            self.load(name)
        self.histories[name].append({"role": role, "content": content})

    def get(self, name):
        return self.histories.get(name) or self.load(name)

# state_manager.py
import json

class StateManager:
    def __init__(self, data):
        self.data = data
    @classmethod
    def load(cls, path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {'balance': None, 'positions': []}
        return cls(data)
    def update(self, balance, positions):
        self.data['balance'] = balance
        self.data['positions'] = positions
    @staticmethod
    def save(path, data):
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

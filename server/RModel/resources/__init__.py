import os
from importlib import import_module

path = os.path.dirname(os.path.abspath(__file__))
for name in os.listdir(path):
    if (name.endswith('.py') or os.path.isdir(name)) and not name.startswith('__'):
        print(name)
        import_module(name.strip('.py'))

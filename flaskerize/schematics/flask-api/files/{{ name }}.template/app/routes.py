import os
from importlib import import_module


def register_routes(api, root="/api"):
    root_dir = os.path.dirname(__file__)
    main_name = os.path.splitext(os.path.basename(root_dir))[0]
    for name in os.listdir(root_dir):
        if name.endswith("test") or not os.path.isdir(os.path.join(root_dir, name)):
            continue
        imported_module = import_module(f"{main_name}.{name}")
        imported_module.register_routes(api, root)

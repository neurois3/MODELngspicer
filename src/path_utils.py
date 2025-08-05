import os

# Converts a relative file path into an absolute path
def get_absolute_path(current_file:str, relative_path:str) -> str:
    base_dir = os.path.dirname(os.path.abspath(current_file))
    absolute_path = os.path.join(base_dir, relative_path)
    return os.path.abspath(absolute_path)

# utils.py
import os
import shutil

def clear_folder(folder_path):
    if not os.path.exists(folder_path):
        return

    if not os.listdir(folder_path):
        return

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.unlink(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)
    
    


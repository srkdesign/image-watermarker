import os
import platform
import subprocess

def open_input_folder(path):
  if not os.path.isdir(path):
    print(f"Folder doesn't exist: {path}")
    return False
  
  system = platform.system()
  try:
    if system == "Windows":
      os.startfile(path)
    elif system == "Darwin":
      subprocess.Popen(["open", path])
    else:
      subprocess.Popen(["xdg-open", path])
    return True
  except Exception as e:
    print(f"Error opening folder: {e}")
    return False

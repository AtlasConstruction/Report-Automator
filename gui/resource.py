import sys
import os
import ctypes

def resource_path(relative_path):
    """ Get absolute path to resource for PyInstaller """
   
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
       
    except Exception:
        base_path = os.path.abspath(".")
        
    path = os.path.join(base_path,'assets', relative_path)
    print(path)
    return path

def setIcon(root):
    # Set the icon (Windows + taskbar fix)
    if sys.platform == 'win32':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('MyCompany.GreetingApp.1')  # Unique ID
    root.iconbitmap(resource_path("atlas.ico"))  # Forces icon in taskbar

def get_chromedriver_path():
    """Get the correct chromedriver path for both development and packaged app"""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
        return os.path.join(base_path, 'drivers', 'chromedriver.exe')
    else:
        # Running in development
        return os.path.join('drivers', 'chromedriver.exe')
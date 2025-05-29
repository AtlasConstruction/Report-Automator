print(" ****** GUI Resource Test ******")
from gui.resource import resource_path

try:
    resource_path("atlas.ico")
except Exception:
    print(Exception)


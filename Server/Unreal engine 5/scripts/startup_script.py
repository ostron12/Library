import sys
sys.path.append('C:/Users/loved/Documents/Unreal Projects/Python_TestV1/Content/scripts')

import importlib
import unreal_server

def start_server():
    importlib.reload(unreal_server)
    unreal_server.start_server()

def stop_server():
    importlib.reload(unreal_server)
    unreal_server.stop_server()

start_server()

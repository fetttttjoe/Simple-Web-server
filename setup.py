from cx_Freeze import setup, Executable
from datetime import date
import os
#
# Folders to include
# Note: possible to add files if in same folder as setup.py
#
programName = "RemoteControl"
programPath = f"{os.path.abspath('.')}/{programName}"
includeFiles = [    
                f"{programPath}/templates",
                f"{programPath}/static", 
                f"{programPath}/util",
                f"{programPath}/certificates" ]

today = date.today()
d = today.strftime("%m/%d/%Y")

executable = Executable(script="startServer.py", target_name=f"{programName}.exe")

setup(name = programName,
      version="0.1",
      description= f"RemoteControl BuildDate: {d}",
      options={
      'build_exe': {
          'build_exe' : f'build/{programName}',
          'packages': [
                        'jinja2',
                        'jinja2.ext',
                        'sys',
                        'os'],
          'include_files': includeFiles,
          'include_msvcr': True}},
      executables=[executable], requires=['flask'])